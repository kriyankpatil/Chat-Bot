"""
Text preprocessing module for cleaning and normalizing text data.
"""
import re
# Commented out spaCy import as it's causing installation issues
# import spacy

class TextPreprocessor:
    """
    Class to preprocess text data for better rule matching and structuring.
    """
    
    def __init__(self, lang="en_core_web_sm"):
        """
        Initialize the preprocessor with a spaCy language model.
        
        Args:
            lang (str): spaCy language model to use
        """
        # Commented out spaCy loading
        # self.nlp = spacy.load(lang)
        pass
    
    def preprocess(self, text, lowercase=True, remove_stopwords=True, lemmatize=True):
        """
        Preprocess text by applying various NLP techniques.
        
        Args:
            text (str): Input text to preprocess
            lowercase (bool): Whether to convert text to lowercase
            remove_stopwords (bool): Whether to remove stopwords
            lemmatize (bool): Whether to apply lemmatization
            
        Returns:
            str: Preprocessed text
        """
        # Simple implementation without spaCy
        if lowercase:
            text = text.lower()
            
        # Simple tokenization by whitespace
        tokens = text.split()
        
        # A basic set of stopwords
        stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
                    'for', 'in', 'to', 'at', 'by', 'is', 'are', 'was', 'were', 'be', 'been',
                    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'of', 'with', 'this',
                    'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my',
                    'your', 'his', 'her', 'its', 'our', 'their'}
        
        if remove_stopwords:
            tokens = [token for token in tokens if token.lower() not in stopwords]
            
        return " ".join(tokens)
    
    def extract_entities(self, text):
        """
        Extract named entities from text.
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Dictionary with entity types as keys and lists of entities as values
        """
        # Simplified version without spaCy
        return {"SIMPLIFIED": ["entity extraction not available without spaCy"]}
    
    def extract_sentences(self, text):
        """
        Split text into sentences.
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of sentences
        """
        # Simple sentence splitting by periods, exclamation marks, or question marks
        return re.split(r'(?<=[.!?])\s+', text)
    
    def normalize_section_id(self, section_id):
        """
        Normalize section identifiers to handle various formats.
        
        Args:
            section_id (str): The section identifier (e.g., "3A", "3a", "3A.")
            
        Returns:
            list: List of possible normalized formats of the section ID
        """
        if not section_id:
            return []
            
        # Generate different variations of the section ID
        variations = [
            section_id,
            section_id.upper(),
            section_id.lower(),
            section_id.strip('.'),
            section_id.upper().strip('.'),
            section_id.lower().strip('.'),
        ]
        
        # Add versions with period if not present
        if '.' not in section_id:
            variations.extend([
                f"{section_id}.",
                f"{section_id.upper()}.",
                f"{section_id.lower()}."
            ])
            
        return list(set(variations))  # Remove duplicates
    
    def extract_section_queries(self, query):
        """
        Extract section identifiers from queries like "what is 3A" or "section 3A".
        
        Args:
            query (str): The user query
            
        Returns:
            tuple: (is_section_query, normalized_section_ids)
        """
        # Check for patterns asking about sections
        section_patterns = [
            r'what\s+is\s+(?:section\s+)?(\d+[A-Za-z]*)',
            r'tell\s+(?:me\s+)?(?:about\s+)?(?:section\s+)?(\d+[A-Za-z]*)',
            r'section\s+(\d+[A-Za-z]*)',
            r'(?:^|\s)(\d+[A-Za-z]*)(?:\s|$)'
        ]
        
        for pattern in section_patterns:
            match = re.search(pattern, query.lower())
            if match:
                section_id = match.group(1)
                normalized_ids = self.normalize_section_id(section_id)
                return True, normalized_ids
                
        return False, []
        
    def clean_text(self, text):
        """
        Clean text by removing special characters, extra whitespace, etc.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Cleaned text
        """
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text 