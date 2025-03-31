"""
Test script for the RAG-based chatbot.
"""
import os
import re
from dotenv import load_dotenv
from app.modules.text_extractor import TextExtractor
from app.modules.text_structurer import TextStructurer
from app.modules.vector_retriever import VectorRetriever
from app.modules.rag_chatbot import RagChatbot

# Load environment variables for API keys
load_dotenv()

def prepare_knowledge_base():
    """
    Prepare the knowledge base by extracting text from sample files
    and chunking it for RAG.
    
    Returns:
        list: List of text chunks
    """
    # Extract text from sample file
    extractor = TextExtractor()
    sample_file = "app/data/sample_rules.txt"
    
    if not os.path.exists(sample_file):
        print(f"Sample file {sample_file} not found.")
        return []
        
    text = extractor.extract_from_text_file(sample_file)
    print(f"Extracted {len(text)} characters of text from the sample file.")
    
    # Chunk the text for RAG
    structurer = TextStructurer()
    
    # Try rule-based chunking first
    chunks = structurer.chunk_by_rules(text)
    print(f"Created {len(chunks)} rule-based chunks.")
    
    # If no chunks were created, fall back to size-based chunking
    if not chunks:
        chunks = structurer.chunk_by_size(text, chunk_size=300, overlap=50)
        print(f"Created {len(chunks)} size-based chunks.")
        
    # Print the first few chunks for inspection
    print("\nSample chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(chunk[:150] + "..." if len(chunk) > 150 else chunk)
        
    return chunks

def initialize_rag_chatbot(chunks):
    """
    Initialize the RAG chatbot with the prepared chunks.
    
    Args:
        chunks (list): List of text chunks
        
    Returns:
        RagChatbot: Initialized RAG chatbot
    """
    # Initialize the vector retriever
    try:
        retriever = VectorRetriever(model_name='all-MiniLM-L6-v2')
        
        if retriever.is_available():
            # Add chunks to the retriever
            retriever.add_chunks(chunks)
            
            # Save the index for future use
            os.makedirs("app/data/vector_index", exist_ok=True)
            retriever.save_index("app/data/vector_index")
            
            print("Vector retriever initialized successfully.")
        else:
            print("Vector retriever not available, will use fallback methods.")
    except Exception as e:
        print(f"Error initializing vector retriever: {e}")
        retriever = None
        
    # Initialize the RAG chatbot
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("OpenAI API key found.")
    else:
        print("OpenAI API key not found. Will use retrieval-only or fallback methods.")
        
    chatbot = RagChatbot(retriever, api_key)
    
    # Set up fallback rules for when RAG isn't available
    fallback_rules = {}
    for i, chunk in enumerate(chunks):
        # Extract keywords for fallback matching
        words = chunk.lower().split()
        keywords = [word for word in words if len(word) > 4 and word.isalpha()]
        fallback_rules[f"chunk_{i}"] = {
            'text': chunk,
            'keywords': keywords[:5] if keywords else []
        }
    
    chatbot.load_rules_for_fallback(fallback_rules)
    print(f"Loaded {len(fallback_rules)} rules for fallback matching.")
    
    return chatbot

def test_rag_chatbot(chatbot):
    """
    Test the RAG chatbot with sample queries.
    
    Args:
        chatbot (RagChatbot): Initialized RAG chatbot
    """
    # Sample queries to test
    test_queries = [
        "How many days notice do I need to give for leave?",
        "What's the process for expense reimbursement?",
        "Do I need approval for expenses over $300?",
        "When do I need to complete compliance training?",
        "What happens if I disclose confidential information?"
    ]
    
    for query in test_queries:
        print(f"\n\nQUERY: {query}")
        
        # Get response using RAG
        response = chatbot.answer_query(query)
        
        print(f"Answer ({response['method']}): {response['answer']}")
        
        if response['chunks']:
            print(f"\nRelevant chunks ({len(response['chunks'])}):")
            for i, chunk in enumerate(response['chunks']):
                print(f"\n- Chunk {i+1}: {chunk[:150]}..." if len(chunk) > 150 else f"\n- Chunk {i+1}: {chunk}")

if __name__ == "__main__":
    print("=== PREPARING KNOWLEDGE BASE ===")
    chunks = prepare_knowledge_base()
    
    if chunks:
        print("\n\n=== INITIALIZING RAG CHATBOT ===")
        chatbot = initialize_rag_chatbot(chunks)
        
        print("\n\n=== TESTING RAG CHATBOT ===")
        test_rag_chatbot(chatbot)
    else:
        print("Failed to prepare knowledge base. Cannot proceed with chatbot testing.") 