"""
Text structuring module for organizing unstructured text into structured formats.
"""
import json
import re
import csv
from collections import defaultdict

class TextStructurer:
    """
    Class to structure text data by organizing it into JSON, CSV, or other formats
    based on keywords, patterns, or rules.
    """
    
    @staticmethod
    def structure_by_keywords(text, keywords, case_sensitive=False):
        """
        Structure text by finding segments that contain specific keywords.
        
        Args:
            text (str): Input text to structure
            keywords (list): List of keywords to search for
            case_sensitive (bool): Whether to perform case-sensitive matching
            
        Returns:
            dict: Dictionary with keywords as keys and matching text segments as values
        """
        structured_data = {}
        
        # Process the text and keywords based on case sensitivity
        processed_text = text if case_sensitive else text.lower()
        processed_keywords = keywords if case_sensitive else [k.lower() for k in keywords]
        
        # Search for each keyword in the text
        for i, keyword in enumerate(processed_keywords):
            if keyword in processed_text:
                # Use the original keyword as the key
                original_keyword = keywords[i]
                structured_data[original_keyword] = text
                
        return structured_data
    
    @staticmethod
    def structure_by_rules(text, rule_patterns):
        """
        Structure text by applying regex patterns to identify rule-based content.
        
        Args:
            text (str): Input text to structure
            rule_patterns (dict): Dictionary mapping rule types to regex patterns
            
        Returns:
            dict: Dictionary with rule types as keys and matching rules as values
        """
        structured_rules = defaultdict(list)
        
        for rule_type, pattern in rule_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                structured_rules[rule_type].append(match.group(0))
                
        return dict(structured_rules)
    
    @staticmethod
    def split_into_sentences(text):
        """
        Split text into individual sentences.
        
        Args:
            text (str): Input text to split
            
        Returns:
            list: List of sentences
        """
        # Simple rule-based sentence splitting
        # Look for period, question mark, or exclamation mark followed by space
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Remove empty sentences and whitespace
        return [s.strip() for s in sentences if s.strip()]
        
    @staticmethod
    def extract_keywords(text):
        """
        Extract important keywords from text.
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of keywords
        """
        # This is a simplified approach to keyword extraction
        # For a real system, consider using techniques like TF-IDF or NLP models
        
        # Define common stopwords to filter out
        stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
                    'when', 'where', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
                    'some', 'such', 'no', 'nor', 'too', 'very', 'can', 'will', 'just',
                    'should', 'now', 'to', 'from', 'of', 'for', 'with', 'by', 'about',
                    'against', 'between', 'into', 'through', 'during', 'before', 'after',
                    'above', 'below', 'on', 'off', 'over', 'under', 'again', 'further',
                    'then', 'once', 'here', 'there', 'why', 'how', 'is', 'are', 'was',
                    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
                    'does', 'did', 'doing', 'this', 'that', 'these', 'those', 'which'}
        
        # Tokenize text (convert to lowercase and split by non-alphanumeric characters)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stopwords and get the most common words
        filtered_words = [word for word in words if word not in stopwords]
        
        # Count word frequency
        word_freq = defaultdict(int)
        for word in filtered_words:
            word_freq[word] += 1
            
        # Sort words by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Extract the top keywords (up to 5)
        keywords = [word for word, freq in sorted_words[:5]]
        
        return keywords

    @staticmethod
    def extract_rules_from_text(text):
        """
        Extract rules from text and structure them.
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Dictionary of rules with IDs and content
        """
        # Default patterns for identifying rules
        rule_patterns = {
            'policy': r'(?i)(?:policy|policies)[\s\:]+(.*?)(?:\.|$)',
            'procedure': r'(?i)(?:procedure|process)[\s\:]+(.*?)(?:\.|$)',
            'requirement': r'(?i)(?:require|requirement|must|shall)[\s\:]+(.*?)(?:\.|$)',
            'rule': r'(?i)(?:rule\s+\d+[\.\d]*|rule)[\s\:]+(.*?)(?:\.|$)'
        }
        
        # Get rules using structure_by_rules
        structured_rules = TextStructurer.structure_by_rules(text, rule_patterns)
        
        # Create a dictionary for the rules
        rules_dict = {}
        rule_id_counter = 1
        
        # Process each rule type
        for rule_type, rules in structured_rules.items():
            for rule_text in rules:
                rule_id = f"{rule_type}_{rule_id_counter}"
                keywords = TextStructurer.extract_keywords(rule_text)
                
                rules_dict[rule_id] = {
                    'text': rule_text,
                    'type': rule_type,
                    'keywords': keywords
                }
                rule_id_counter += 1
                
        # If no rules found, fall back to paragraphs
        if not rules_dict:
            paragraphs = re.split(r'\n\s*\n', text)
            for i, paragraph in enumerate(paragraphs, 1):
                if len(paragraph.strip()) > 20:  # Only consider substantial paragraphs
                    rule_id = f"paragraph_{i}"
                    keywords = TextStructurer.extract_keywords(paragraph)
                    
                    rules_dict[rule_id] = {
                        'text': paragraph.strip(),
                        'type': 'paragraph',
                        'keywords': keywords
                    }
                    
        return rules_dict
    
    @staticmethod
    def to_json(structured_data, file_path=None, indent=4):
        """
        Convert structured data to JSON format.
        
        Args:
            structured_data (dict): Structured data to convert
            file_path (str, optional): Path to save the JSON file
            indent (int): JSON indentation level
            
        Returns:
            str: JSON string representation
        """
        json_str = json.dumps(structured_data, indent=indent)
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(json_str)
                
        return json_str
    
    @staticmethod
    def to_csv(structured_data, file_path, headers=None):
        """
        Convert structured data to CSV format.
        
        Args:
            structured_data (list): List of dictionaries to convert to CSV
            file_path (str): Path to save the CSV file
            headers (list, optional): List of column headers
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not structured_data:
            return False
            
        if not headers and isinstance(structured_data[0], dict):
            headers = structured_data[0].keys()
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(structured_data)
            return True
        except Exception as e:
            print(f"Error writing CSV: {e}")
            return False
            
    @staticmethod
    def chunk_by_size(text, chunk_size=500, overlap=100):
        """
        Chunk text into fixed-size chunks with overlap.
        
        Args:
            text (str): Input text to chunk
            chunk_size (int): Maximum size of each chunk
            overlap (int): Number of characters to overlap between chunks
            
        Returns:
            list: List of text chunks
        """
        chunks = []
        
        if len(text) <= chunk_size:
            return [text]
            
        start = 0
        while start < len(text):
            # Find the end of the chunk
            end = min(start + chunk_size, len(text))
            
            # If we're not at the end of the text, try to find a natural breaking point
            if end < len(text):
                # Look for a period, question mark, or exclamation mark followed by a space
                natural_break = max(
                    text.rfind('. ', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('\n', start, end)
                )
                
                # If we found a natural break, use it
                if natural_break != -1:
                    end = natural_break + 2  # Include the period and space
            
            # Add the chunk to our list
            chunks.append(text[start:end].strip())
            
            # Move to the next chunk, with overlap
            start = max(start + 1, end - overlap)
            
        return chunks
        
    @staticmethod
    def chunk_by_rules(text, rule_patterns=None):
        """
        Chunk text by extracting rules and policies.
        
        Args:
            text (str): Input text to chunk
            rule_patterns (dict, optional): Dictionary of rule patterns
            
        Returns:
            list: List of rule chunks
        """
        if rule_patterns is None:
            # Default patterns for common rule formats
            rule_patterns = {
                'policy': r'Policy\s+\d+[\.\d]*:\s+.+?(?=\n\n|\n(?:Policy|Procedure|Rule)\s+\d+|\Z)',
                'procedure': r'Procedure\s+\d+[\.\d]*:\s+.+?(?=\n\n|\n(?:Policy|Procedure|Rule)\s+\d+|\Z)',
                'rule': r'Rule\s+\d+[\.\d]*:\s+.+?(?=\n\n|\n(?:Policy|Procedure|Rule)\s+\d+|\Z)',
                'section': r'SECTION\s+\d+[\.\d]*:\s+.+?(?=\n\nSECTION\s+\d+|\Z)'
            }
            
        chunks = []
        
        # Extract chunks based on each pattern
        for pattern_name, pattern in rule_patterns.items():
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                chunk = match.group(0).strip()
                if chunk:
                    chunks.append(chunk)
                    
        # If no rule-based chunks found, fall back to chunking by paragraphs
        if not chunks:
            paragraphs = re.split(r'\n\s*\n', text)
            chunks = [p.strip() for p in paragraphs if p.strip()]
            
        return chunks 