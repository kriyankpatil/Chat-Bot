"""
Vector retriever module for embedding and retrieving text chunks.
"""
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

class VectorRetriever:
    """
    Class for embedding text chunks and retrieving the most similar chunks for a query.
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the vector retriever with a sentence transformer model.
        
        Args:
            model_name (str): Name of the sentence-transformers model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.chunks = []
            self.index = None
            self.dimension = None
        except Exception as e:
            print(f"Error initializing vector retriever: {e}")
            # Set up a fallback to keyword-based matching if model loading fails
            self.model = None
            
    def is_available(self):
        """
        Check if the vector retriever model is available.
        
        Returns:
            bool: True if the model is available, False otherwise
        """
        return self.model is not None
            
    def add_chunks(self, chunks):
        """
        Add text chunks to the retriever and build the FAISS index.
        
        Args:
            chunks (list): List of text chunks to add
        """
        if not self.model:
            print("Vector retriever model not available, cannot add chunks")
            return
            
        # Remove any extremely long chunks (likely full documents)
        filtered_chunks = []
        for chunk in chunks:
            # Split very long chunks into smaller ones if needed
            if len(chunk) > 1000:
                # Try to find natural break points at sentence endings
                sentences = [s.strip() + '.' for s in chunk.split('.') if s.strip()]
                current_segment = ""
                
                for sentence in sentences:
                    if len(current_segment) + len(sentence) < 500:
                        current_segment += " " + sentence
                    else:
                        if current_segment:
                            filtered_chunks.append(current_segment.strip())
                        current_segment = sentence
                
                if current_segment:  # Add the last segment
                    filtered_chunks.append(current_segment.strip())
            else:
                filtered_chunks.append(chunk)
                
        self.chunks = filtered_chunks
        
        # Encode all chunks to vector embeddings
        embeddings = self.model.encode(filtered_chunks)
        self.dimension = embeddings.shape[1]
        
        # Create a FAISS index for fast similarity search
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        print(f"Added {len(filtered_chunks)} chunks to vector retriever")
        
    def retrieve(self, query, top_k=3):
        """
        Retrieve the most relevant chunks for a query.
        
        Args:
            query (str): The query text
            top_k (int): Number of top chunks to retrieve
            
        Returns:
            list: List of most relevant text chunks
        """
        if not self.model or not self.index:
            print("Vector retriever model or index not available, cannot retrieve")
            return []
            
        # Extract key terms from the query for additional filtering
        query_terms = set([term.lower() for term in query.split() if len(term) > 2])  # Reduced minimum term length
        
        # Encode the query to a vector embedding
        query_embedding = self.model.encode([query])
        
        # Search the FAISS index for similar chunks - get more than we need for post-filtering
        initial_k = min(top_k * 3, len(self.chunks))  # Increased initial retrieval
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'), 
            initial_k
        )
        
        # Define a maximum distance (L2 distance) threshold
        # Higher L2 distance means less similar, so we want to reject those above the threshold
        max_distance_threshold = 1.8  # Adjust based on testing - smaller values make matching stricter
        
        # Post-process results by checking term overlap and deduplicating similar content
        filtered_chunks = []
        seen_content = set()
        
        for i, dist in zip(indices[0], distances[0]):
            # Skip chunks with distance above threshold
            if dist > max_distance_threshold:
                continue
                
            chunk = self.chunks[i]
            
            # Create a simple hash of content to avoid nearly identical chunks
            content_hash = ' '.join(sorted(chunk.lower().split())[:20])
            
            # Skip if we've seen very similar content
            if content_hash in seen_content:
                continue
            
            # Calculate overlap with query terms
            chunk_terms = set([term.lower() for term in chunk.split() if len(term) > 2])  # Reduced minimum term length
            term_overlap = len(query_terms.intersection(chunk_terms))
            
            # Prioritize chunks with term overlap but don't exclude chunks without overlap
            if term_overlap > 0 or len(filtered_chunks) < top_k:
                filtered_chunks.append(chunk)
                seen_content.add(content_hash)
                
                if len(filtered_chunks) >= top_k:
                    break
        
        # If we didn't get enough chunks, fall back to original order but still respect distance threshold
        if not filtered_chunks and indices.size > 0:
            for i, dist in zip(indices[0], distances[0]):
                if dist <= max_distance_threshold and len(filtered_chunks) < top_k:
                    filtered_chunks.append(self.chunks[i])
            
        return filtered_chunks
    
    def save_index(self, directory):
        """
        Save the FAISS index and chunks to disk.
        
        Args:
            directory (str): Directory to save the index and chunks
        """
        if not self.model or not self.index:
            print("Vector retriever model or index not available, cannot save")
            return
            
        os.makedirs(directory, exist_ok=True)
        
        # Save the FAISS index
        faiss.write_index(self.index, os.path.join(directory, "index.faiss"))
        
        # Save the chunks
        with open(os.path.join(directory, "chunks.txt"), "w", encoding="utf-8") as f:
            for chunk in self.chunks:
                f.write(chunk + "\n===CHUNK_SEPARATOR===\n")
                
        print(f"Saved vector index and {len(self.chunks)} chunks to {directory}")
        
    def load_index(self, directory):
        """
        Load the FAISS index and chunks from disk.
        
        Args:
            directory (str): Directory containing the saved index and chunks
        """
        if not self.model:
            print("Vector retriever model not available, cannot load index")
            return
            
        index_path = os.path.join(directory, "index.faiss")
        chunks_path = os.path.join(directory, "chunks.txt")
        
        if os.path.exists(index_path) and os.path.exists(chunks_path):
            # Load the FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load the chunks
            with open(chunks_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.chunks = content.split("\n===CHUNK_SEPARATOR===\n")[:-1]  # Remove the last empty chunk
                
            print(f"Loaded vector index and {len(self.chunks)} chunks from {directory}")
            return True
        else:
            print(f"Index or chunks file not found in {directory}")
            return False 