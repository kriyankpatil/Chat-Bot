"""
Rule matching module for identifying relevant rules based on user queries.
"""
import re
from collections import defaultdict

class RuleMatcher:
    """
    Class to match user queries with relevant rules from a structured rule database.
    """
    
    def __init__(self):
        """
        Initialize the rule matcher with an empty rule database.
        """
        self.rules = {}
        self.rule_keywords = defaultdict(list)
        
    def add_rule(self, rule_id, rule_text, keywords=None):
        """
        Add a rule to the rule database.
        
        Args:
            rule_id (str): Unique identifier for the rule
            rule_text (str): The rule text content
            keywords (list, optional): List of keywords associated with this rule
        """
        self.rules[rule_id] = rule_text
        
        if keywords:
            for keyword in keywords:
                self.rule_keywords[keyword.lower()].append(rule_id)
                
    def load_rules_from_dict(self, rules_dict):
        """
        Load rules from a dictionary.
        
        Args:
            rules_dict (dict): Dictionary with rule_id as keys and rule content as values
        """
        for rule_id, rule_data in rules_dict.items():
            if isinstance(rule_data, dict):
                rule_text = rule_data.get('text', '')
                keywords = rule_data.get('keywords', [])
            else:
                rule_text = rule_data
                keywords = []
                
            self.add_rule(rule_id, rule_text, keywords)
            
    def match_by_keywords(self, query, case_sensitive=False, threshold=0):
        """
        Match user query with rules based on keyword matching.
        
        Args:
            query (str): User query text
            case_sensitive (bool): Whether to perform case-sensitive matching
            threshold (int): Minimum number of keyword matches required
            
        Returns:
            dict: Dictionary of matching rule_ids and their rule texts
        """
        processed_query = query if case_sensitive else query.lower()
        matched_rules = defaultdict(int)
        
        # Count keyword matches for each rule
        for keyword, rule_ids in self.rule_keywords.items():
            keyword_to_match = keyword if case_sensitive else keyword.lower()
            if keyword_to_match in processed_query:
                for rule_id in rule_ids:
                    matched_rules[rule_id] += 1
        
        # Filter rules that meet the threshold
        result = {}
        for rule_id, match_count in matched_rules.items():
            if match_count > threshold:
                result[rule_id] = self.rules[rule_id]
                
        return result
    
    def match_by_regex(self, query, patterns):
        """
        Match user query with rules based on regex patterns.
        
        Args:
            query (str): User query text
            patterns (dict): Dictionary mapping pattern names to regex patterns
            
        Returns:
            dict: Dictionary of matching pattern names and their matching rule_ids
        """
        matches = {}
        
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, query):
                # Find rules that match this pattern
                matching_rules = {}
                for rule_id, rule_text in self.rules.items():
                    if re.search(pattern, rule_text):
                        matching_rules[rule_id] = rule_text
                
                if matching_rules:
                    matches[pattern_name] = matching_rules
                    
        return matches
    
    def get_rule(self, rule_id):
        """
        Get a specific rule by its ID.
        
        Args:
            rule_id (str): Rule identifier
            
        Returns:
            str: Rule text if found, None otherwise
        """
        return self.rules.get(rule_id)
        
    def reset_rules(self):
        """
        Reset all rules and keywords in the matcher.
        """
        self.rules = {}
        self.rule_keywords = defaultdict(list) 