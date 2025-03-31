"""
Test script for the rule-based chatbot.
"""
import os
import re
from app.modules.text_extractor import TextExtractor
from app.modules.text_preprocessor import TextPreprocessor
from app.modules.text_structurer import TextStructurer
from app.modules.rule_matcher import RuleMatcher

def test_rule_extraction():
    """
    Test extracting rules from sample data.
    """
    # Extract text from the sample file
    extractor = TextExtractor()
    sample_file = "app/data/sample_rules.txt"
    
    if not os.path.exists(sample_file):
        print(f"Sample file {sample_file} not found.")
        return
        
    text = extractor.extract_from_text_file(sample_file)
    print(f"Extracted {len(text)} characters of text from the sample file.")
    
    # Manually extract rules for testing
    policies = re.findall(r'Policy\s+\d+\.\d+:\s+(.*?)(?=\n\n|\Z)', text, re.DOTALL)
    procedures = re.findall(r'Procedure\s+\d+\.\d+:\s+(.*?)(?=\n\n|\Z)', text, re.DOTALL)
    rules = re.findall(r'Rule\s+\d+\.\d+:\s+(.*?)(?=\n\n|\Z)', text, re.DOTALL)
    
    structured_rules = {
        'policy': policies,
        'procedure': procedures,
        'rule': rules
    }
    
    print(f"Extracted {sum(len(rules) for rules in structured_rules.values())} rules:")
    
    for rule_type, rule_list in structured_rules.items():
        print(f"\n{rule_type.upper()} RULES:")
        for i, rule in enumerate(rule_list, 1):
            print(f"{i}. {rule.strip()}")
    
    # Extract rules by keywords
    print("\nTEST KEYWORD EXTRACTION:")
    keywords = ['leave', 'reimbursement', 'approval', 'training']
    
    # Create a TextStructurer instance
    structurer = TextStructurer()
    keyword_rules = structurer.structure_by_keywords(text, keywords)
    
    for keyword, matching_text in keyword_rules.items():
        print(f"\nRules containing '{keyword}':")
        # Extract just a snippet containing the keyword for demonstration
        index = matching_text.lower().find(keyword.lower())
        start = max(0, index - 50)
        end = min(len(matching_text), index + 50)
        print(f"...{matching_text[start:end]}...")
        
def test_chatbot_queries():
    """
    Test the chatbot with sample queries.
    """
    # Setup the rule matcher with rules from the sample file
    matcher = RuleMatcher()
    extractor = TextExtractor()
    
    sample_file = "app/data/sample_rules.txt"
    if not os.path.exists(sample_file):
        print(f"Sample file {sample_file} not found.")
        return
        
    # Extract the text without preprocessing for better rule extraction
    text = extractor.extract_from_text_file(sample_file)
    
    # Extract relevant sections and add them as rules
    sections = {
        'leave': r'SECTION 1:\s+LEAVE POLICIES(.*?)(?=SECTION \d+:|$)',
        'reimbursement': r'SECTION 2:\s+REIMBURSEMENT POLICIES(.*?)(?=SECTION \d+:|$)',
        'compliance': r'SECTION 3:\s+COMPLIANCE REQUIREMENTS(.*?)(?=SECTION \d+:|$)'
    }
    
    # Add each section as a rule
    for section_name, pattern in sections.items():
        matches = re.finditer(pattern, text, re.DOTALL)
        for i, match in enumerate(matches):
            section_text = match.group(1).strip()
            matcher.add_rule(f"{section_name}_{i}", section_text, [section_name])
    
    # Add specific policies, procedures, and rules
    policies = re.finditer(r'(Policy \d+\.\d+:[^\n]+(?:\n[^\n]+)*)', text)
    for i, match in enumerate(policies):
        policy_text = match.group(1)
        # Extract keywords from the policy text
        words = policy_text.lower().split()
        keywords = [word for word in words if len(word) > 4 and word.isalpha()]
        matcher.add_rule(f"policy_{i}", policy_text, keywords[:5])
        
    procedures = re.finditer(r'(Procedure \d+\.\d+:[^\n]+(?:\n[^\n]+)*)', text)
    for i, match in enumerate(procedures):
        procedure_text = match.group(1)
        words = procedure_text.lower().split()
        keywords = [word for word in words if len(word) > 4 and word.isalpha()]
        matcher.add_rule(f"procedure_{i}", procedure_text, keywords[:5])
        
    rules = re.finditer(r'(Rule \d+\.\d+:[^\n]+(?:\n[^\n]+)*)', text)
    for i, match in enumerate(rules):
        rule_text = match.group(1)
        words = rule_text.lower().split()
        keywords = [word for word in words if len(word) > 4 and word.isalpha()]
        matcher.add_rule(f"rule_{i}", rule_text, keywords[:5])
    
    print(f"Initialized chatbot with {len(matcher.rules)} rules.\n")
    
    # Test with sample queries
    test_queries = [
        "How many days notice do I need to give for leave?",
        "What's the process for expense reimbursement?",
        "Do I need approval for expenses over $300?",
        "When do I need to complete compliance training?",
        "What happens if I disclose confidential information?"
    ]
    
    for query in test_queries:
        print(f"\nQUERY: {query}")
        matched_rules = matcher.match_by_keywords(query)
        
        if matched_rules:
            print(f"Found {len(matched_rules)} matching rules:")
            for rule_id, rule_text in matched_rules.items():
                # Print a shortened version of the rule for readability
                shortened = rule_text[:150] + "..." if len(rule_text) > 150 else rule_text
                print(f"- {shortened}")
        else:
            print("No matching rules found.")
            
if __name__ == "__main__":
    print("=== TESTING RULE EXTRACTION ===")
    test_rule_extraction()
    
    print("\n\n=== TESTING CHATBOT QUERIES ===")
    test_chatbot_queries() 