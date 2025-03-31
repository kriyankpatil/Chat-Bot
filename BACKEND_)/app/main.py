"""
Main application module for the Gujarat Civil Services chatbot backend.

This module demonstrates how to use direct text matching to answer queries about Gujarat Civil Services.
"""
import os
import re
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.modules.text_extractor import TextExtractor
from app.modules.text_preprocessor import TextPreprocessor
import openai

# Load environment variables
load_dotenv()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
documents = {}  # Store text content of all files
sections_map = {}  # Map of section numbers to content for each file

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    selected_file: str = None  # Optional parameter for when user selects a file

class QueryResponse(BaseModel):
    exact_match: str
    ai_response: str
    enhanced_response: str = None
    response: str = None
    file_options: list = None  # List of files that contain relevant information

# File paths
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
print(f"Data directory path: {DATA_DIR}")  # Log the full path

def extract_sections(text, file_id):
    """
    Extract sections from the text and create a mapping of section numbers to their content.
    
    Args:
        text (str): Full text content
        file_id (str): Identifier for the source file
        
    Returns:
        dict: Dictionary mapping section numbers to their content
    """
    # Regular expression to find sections like "3A." or "9AB." followed by a title and content
    section_pattern = r'(\d+[A-Z]*)\.[\s\t]+(.*?)(?=\n\d+[A-Z]*\.|\Z)'
    
    # Find all sections in the text using a more careful approach
    sections = {}
    
    # First, try to identify all possible section IDs from the table of contents
    toc_pattern = r'(\d+[A-Z]*)\.[\s\t]+(.*?)(?=\n|$)'
    toc_sections = re.findall(toc_pattern, text)
    section_ids = [section_id for section_id, _ in toc_sections]
    
    # For each section ID, try to find its content in the document
    for section_id in section_ids:
        # Look for patterns like "3A. Consolidated Allowance to Ministers."
        full_section_pattern = rf'{section_id}\.[\s\t]+(.*?)(?=\n\d+[A-Z]*\.|\Z)'
        matches = re.finditer(full_section_pattern, text, re.DOTALL)
        
        for match in matches:
            section_content = match.group(0).strip()
            # Store both the full section ID and a normalized version (e.g., both "3A" and "3a")
            key = f"{file_id}:{section_id}"
            sections[key] = section_content
            sections[f"{file_id}:{section_id.lower()}"] = section_content
            
            # Also store without the period (e.g., "3A" instead of "3A.")
            sections[f"{file_id}:{section_id.replace('.', '')}"] = section_content
            sections[f"{file_id}:{section_id.lower().replace('.', '')}"] = section_content
    
    # Special search for common section patterns
    for section_match in re.finditer(r'(?:^|\n)(\d+[A-Z]*)\.[\s\t]+(.*?)(?=\n\d+[A-Z]*\.|\Z)', text, re.DOTALL):
        section_id = section_match.group(1)
        section_content = section_match.group(0).strip()
        
        key = f"{file_id}:{section_id}"
        if key not in sections:
            sections[key] = section_content
            sections[f"{file_id}:{section_id.lower()}"] = section_content
            
            # Also store without the period
            sections[f"{file_id}:{section_id.replace('.', '')}"] = section_content
            sections[f"{file_id}:{section_id.lower().replace('.', '')}"] = section_content
    
    return sections

def load_data_files():
    """
    Load all text files from the data directory.
    
    Returns:
        dict: Dictionary mapping file IDs to their text content
    """
    global documents, sections_map
    
    print(f"Attempting to load data files from: {DATA_DIR}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Data directory not found at: {DATA_DIR}")
        # Try to create the data directory
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            print(f"Created data directory at: {DATA_DIR}")
        except Exception as e:
            print(f"Error creating data directory: {str(e)}")
        return {}
    
    file_documents = {}
    all_sections = {}
    
    try:
        extractor = TextExtractor()
        
        # Get all .txt files in the data directory
        try:
            txt_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]
            print(f"Found {len(txt_files)} text files: {txt_files}")
        except Exception as e:
            print(f"Error listing files in data directory: {str(e)}")
            return {}
        
        if not txt_files:
            print("No text files found in the data directory.")
            return {}
        
        # Load each text file
        for file_name in txt_files:
            try:
                file_path = os.path.join(DATA_DIR, file_name)
                file_id = os.path.splitext(file_name)[0]  # Remove extension to get ID
                print(f"Processing file: {file_name} (ID: {file_id})")
                print(f"Full file path: {file_path}")
                
                if not os.path.isfile(file_path):
                    print(f"Warning: {file_path} is not a file or does not exist")
                    continue
                
                text = extractor.extract_from_text_file(file_path)
                
                if text and len(text.strip()) > 0:
                    if isinstance(text, str):
                        file_documents[file_id] = text
                        
                        # Extract sections for this file
                        try:
                            file_sections = extract_sections(text, file_id)
                            all_sections.update(file_sections)
                            print(f"Successfully loaded {len(text)} characters and {len(file_sections)} sections from {file_name}")
                        except Exception as e:
                            print(f"Error extracting sections from {file_name}: {str(e)}")
                    else:
                        print(f"Warning: Extracted content from {file_name} is not a string")
                else:
                    print(f"No text could be extracted from {file_name}")
            except Exception as e:
                print(f"Error processing file {file_name}: {str(e)}")
                continue
        
        sections_map = all_sections
        print(f"Total: Extracted {len(sections_map)} section entries from {len(file_documents)} files")
        
        return file_documents
    except Exception as e:
        print(f"Error loading data files: {str(e)}")
        print(f"Error details: {type(e).__name__}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return {}

def find_relevant_text(query, documents, selected_file=None):
    """
    Find relevant portions of text based on the query across all documents or a specific file.
    
    Args:
        query (str): User query
        documents (dict): Dictionary of document texts
        selected_file (str, optional): If provided, search only in this file
        
    Returns:
        tuple: (relevant_text, file_options)
            - relevant_text: The most relevant text snippet
            - file_options: List of files containing relevant information
    """
    global sections_map
    
    if not documents:
        return "The document information is not available.", []
    
    # Initialize preprocessor for query processing
    preprocessor = TextPreprocessor()
    
    # Normalize query to improve matching
    query_normalized = query.lower().strip()
    
    # First, check if this is a query for a specific section
    is_section_query, section_ids = preprocessor.extract_section_queries(query)
    
    if is_section_query and section_ids:
        # Handle section queries as before...
        # [existing section query code]
        if selected_file:
            # Try each of the normalized section IDs in the selected file
            for section_id in section_ids:
                key = f"{selected_file}:{section_id}"
                if key in sections_map:
                    return f"Here's the information about section {section_id} from {selected_file}:\n\n{sections_map[key]}", [selected_file]
            
            # If section wasn't found with normalized IDs, try a more flexible search
            base_section_id = section_ids[0]  # Use first one as the base
            matching_keys = []
            for key in sections_map.keys():
                file_id, sec_id = key.split(":", 1)
                if file_id == selected_file and base_section_id.lower() in sec_id.lower():
                    return f"Here's the information that might be related to section {base_section_id} from {selected_file}:\n\n{sections_map[key]}", [selected_file]
            
            return f"I couldn't find any specific information about section {base_section_id} in {selected_file}. Please try a different query.", []
        
        # If no file is selected, search across all files
        matching_files = {}
        for section_id in section_ids:
            for key in sections_map.keys():
                if section_id in key:
                    file_id = key.split(":", 1)[0]
                    if file_id not in matching_files:
                        matching_files[file_id] = sections_map[key]
        
        if matching_files:
            if len(matching_files) == 1:
                file_id = list(matching_files.keys())[0]
                return f"Here's the information about section {section_ids[0]} from {file_id}:\n\n{matching_files[file_id]}", [file_id]
            else:
                file_ids = list(matching_files.keys())
                return f"I found information about section {section_ids[0]} in multiple files. Please select which file you want to get information from.", file_ids
        
        return f"I couldn't find any specific information about section {section_ids[0]}. Please try a different query.", []
    
    # Check if query is looking for a specific section title
    # This handles queries like "Give me all points in SECTION NAME"
    section_title_patterns = [
        r"(?:information|details|points|content) (?:about|on|in|for|regarding) (.+)$",
        r"tell me about (.+)$",
        r"what (?:is|are) (.+)$",
        r"show me (.+)$",
        r"give me (?:all|the) (?:information|details|points|content) (?:about|on|in|for|regarding) (.+)$"
    ]
    
    potential_section_title = None
    for pattern in section_title_patterns:
        match = re.search(pattern, query_normalized, re.IGNORECASE)
        if match:
            potential_section_title = match.group(1).strip()
            print(f"Potential section title extracted: '{potential_section_title}'")
            break
    
    # Check if query explicitly mentions a specific file or topic
    query_lower = query.lower()
    
    # Map of keywords to specific files (without .txt extension)
    file_keywords = {
        "Gujarat_Ministers_Salaries_and_All": ["minister", "salary", "allowance", "ministers", "salaries", "allowances"],
        "Gujarat Civil Services Rules": ["civil service", "service rules", "civil services rules", "civil servant", "recruitment", "appointment"],
        "The Gujarat Civil Services (Discipl": ["disciplinary", "discipline", "misconduct", "penalty", "punishment"]
    }
    
    # Check if query contains keywords that map to a specific file
    matched_files = []
    for file_id, keywords in file_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            matched_files.append(file_id)
    
    # If query specifically mentions only one file's keywords, prioritize that file
    if len(matched_files) == 1 and not selected_file:
        selected_file = matched_files[0]
        print(f"Auto-selecting file based on keywords: {selected_file}")
    
    # If not a specific section query, proceed with regular search
    # Preprocess the query
    query_cleaned = preprocessor.clean_text(query.lower())
    
    # Extract keywords from query
    keywords = [word for word in query_cleaned.split() if len(word) > 3]
    
    # If we found a potential section title, add its words as high-priority keywords
    if potential_section_title:
        # Add the entire phrase as one keyword for exact matching
        section_title_words = potential_section_title.split()
        keywords.extend([word for word in section_title_words if len(word) > 2])
        
        # Also add the entire phrase as a special keyword for exact matching
        keywords.append(potential_section_title)
    
    # If no good keywords, use all words
    if not keywords:
        keywords = query_cleaned.split()
    
    # Search in the selected file or across all files
    file_matches = {}
    exact_title_matches = {}
    
    if selected_file:
        # Only search in the selected file
        search_docs = {selected_file: documents[selected_file]} if selected_file in documents else {}
    else:
        # Search across all files
        search_docs = documents
    
    # Try exact matching for the potential section title first
    if potential_section_title:
        title_upper = potential_section_title.upper()
        title_lower = potential_section_title.lower()
        title_capitalized = potential_section_title.title()
        
        for file_id, text in search_docs.items():
            # Check for exact matches or close variants of the section title
            for variant in [potential_section_title, title_upper, title_lower, title_capitalized]:
                if variant in text:
                    # Find the paragraph containing the section title
                    paragraphs = re.split(r'\n\s*\n', text)
                    for paragraph in paragraphs:
                        if variant in paragraph:
                            # Found exact match for the section title
                            print(f"Found exact section title match in {file_id}: '{variant}'")
                            # Include a few paragraphs after the title for context
                            start_idx = text.find(paragraph)
                            content_after = text[start_idx:start_idx+5000]  # Get a good chunk of text after
                            paragraphs_after = re.split(r'\n\s*\n', content_after)[:5]  # Take first 5 paragraphs
                            exact_title_matches[file_id] = (10, "\n\n".join(paragraphs_after))
                            break
    
    # If exact title matches were found, prefer these over regular keyword matches
    if exact_title_matches:
        file_matches = exact_title_matches
    else:
        # Regular keyword-based search
        for file_id, text in search_docs.items():
            # Get paragraphs from the text
            paragraphs = re.split(r'\n\s*\n', text)
            
            # Score paragraphs based on keyword matches
            scored_paragraphs = []
            for paragraph in paragraphs:
                paragraph_lower = paragraph.lower()
                
                # Basic score based on keyword frequency
                keyword_score = sum(1 for keyword in keywords if keyword in paragraph_lower)
                
                # Bonus for exact title match if potential_section_title was found
                title_bonus = 0
                if potential_section_title and potential_section_title in paragraph_lower:
                    title_bonus = 5
                elif potential_section_title and potential_section_title.upper() in paragraph:
                    title_bonus = 5
                
                # Total score
                total_score = keyword_score + title_bonus
                
                if total_score > 0:
                    scored_paragraphs.append((total_score, paragraph))
            
            # Sort paragraphs by score
            scored_paragraphs.sort(reverse=True)
            
            # Store the top matching paragraph for this file if any matches found
            if scored_paragraphs:
                file_matches[file_id] = scored_paragraphs[0]
    
    # If no matches found in any file
    if not file_matches:
        # If a potential section title was identified but no matches were found,
        # try a more flexible search using individual words from the title
        if potential_section_title:
            title_words = [w for w in potential_section_title.split() if len(w) > 3]
            
            if title_words:
                print(f"Trying flexible search with title words: {title_words}")
                for file_id, text in search_docs.items():
                    paragraphs = re.split(r'\n\s*\n', text)
                    scored_paragraphs = []
                    
                    for paragraph in paragraphs:
                        paragraph_lower = paragraph.lower()
                        score = sum(2 for word in title_words if word.lower() in paragraph_lower)
                        
                        if score > 0:
                            scored_paragraphs.append((score, paragraph))
                    
                    scored_paragraphs.sort(reverse=True)
                    if scored_paragraphs:
                        file_matches[file_id] = scored_paragraphs[0]
            
            if not file_matches:
                return f"I couldn't find specific information about '{potential_section_title}'. Please try a different query or check the exact wording.", []
        else:
            return "I couldn't find specific information related to your query. Please try a different question.", []
    
    # If a specific file was selected by the user or auto-selected based on keywords
    if selected_file and selected_file in file_matches:
        return f"Here's information from {selected_file}:\n\n{file_matches[selected_file][1]}", [selected_file]
    
    # Calculate relevance scores for each file
    file_relevance = {}
    for file_id, (score, paragraph) in file_matches.items():
        # Base score from keyword matches
        relevance = score
        
        # Boost score if file was matched by keywords
        if file_id in matched_files:
            relevance += 3
            
        file_relevance[file_id] = relevance
    
    # Find the file with the highest relevance
    if file_relevance:
        best_file_id = max(file_relevance.keys(), key=lambda k: file_relevance[k])
        best_score = file_relevance[best_file_id]
        
        # If one file is significantly more relevant than others (50% better than second best)
        if len(file_relevance) > 1:
            scores = sorted(file_relevance.values(), reverse=True)
            if best_score >= scores[1] * 1.5:  # 50% threshold
                # Just use the best file without asking
                return f"Here's information from {best_file_id}:\n\n{file_matches[best_file_id][1]}", [best_file_id]
        
        # If matches found in multiple files but none is significantly better
        if len(file_matches) > 1:
            # Sort files by relevance score
            sorted_files = sorted(file_relevance.keys(), key=lambda k: file_relevance[k], reverse=True)
            return "I found relevant information in multiple files. Please select which file you want to get information from.", sorted_files
        else:
            # Only one match found
            return f"Here's information from {best_file_id}:\n\n{file_matches[best_file_id][1]}", [best_file_id]
    
    # If no good matches found
    return "I couldn't find specific information related to your query. Please try a different question.", []

def get_ai_response(query, context, file_id=None):
    """
    Generate an AI response based on the query and context.
    
    Args:
        query (str): User query
        context (str): Context from the direct text search
        file_id (str, optional): The ID of the file the context is from
        
    Returns:
        str: AI-generated response
    """
    try:
        file_context = f" from {file_id}" if file_id else ""
        
        prompt = f"""
        QUERY: {query}
        
        CONTEXT{file_context}: {context}
        
        Please provide a focused and precise answer that addresses ONLY what was specifically asked in the query.
        Follow these guidelines:
        
        1. Address ONLY the specific question or request in the query - do not provide surrounding or tangential information
        2. Structure your response with clear headings (## for main headings, ### for subheadings) directly related to the query
        3. Use bullet points or numbered lists to present information clearly when appropriate
        4. Bold (**text**) important terms, rules, or section numbers mentioned
        5. If the query asks for specific points or rules, provide only those points - not surrounding context
        6. If the exact information requested isn't available in the context, state this clearly
        7. Avoid including "introductory" or "background" information unless specifically requested
        
        Remember: Focus ONLY on answering what was directly asked. If asked about a specific section, rule, or topic, limit your answer to that specific item.
        Always cite the source document{file_context} in your response.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert assistant that provides precise, focused information about Gujarat Civil Services rules and regulations, addressing only what was specifically asked."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return f"I found this information{file_context}: {context}"

def get_enhanced_response(query, direct_match, ai_response, file_id=None):
    """
    Generate an enhanced response by synthesizing the direct match and AI response.
    
    Args:
        query (str): User query
        direct_match (str): Direct text match from the search
        ai_response (str): AI-generated response
        file_id (str, optional): The ID of the file the responses are from
        
    Returns:
        str: Enhanced synthesized response
    """
    try:
        file_context = f" from {file_id}" if file_id else ""
        
        prompt = f"""
        QUERY: {query}
        
        DIRECT MATCH{file_context}: {direct_match}
        
        AI RESPONSE: {ai_response}
        
        Please synthesize the information to provide a precise answer that addresses ONLY what was specifically asked in the query.
        Follow these requirements:
        
        1. Focus EXCLUSIVELY on the specific request or question posed - do not include tangential information
        2. Structure your response with headings (## and ###) that directly address the query
        3. Use bullet points or numbered lists to make specific information clear
        4. Bold (**text**) key points, rules, or sections
        5. If the query asks for specific points or requirements, list ONLY those points
        6. Omit any surrounding context or related topics not specifically requested
        7. Do not provide general introductions or background unless explicitly asked
        8. If the exact information requested isn't available, clearly state this
        
        The user has specifically requested that responses contain ONLY the information they asked for, without surrounding topics or general context.
        Always indicate the source document{file_context} in your response.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better synthesis
            messages=[
                {"role": "system", "content": "You are an expert assistant that provides precise, focused responses about Gujarat Civil Services rules and regulations. You address ONLY what was specifically asked without including surrounding topics or general context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.2
        )
        
        # Extract the synthesized answer from the response
        synthesized_answer = response.choices[0].message.content.strip()
        return synthesized_answer
    
    except Exception as e:
        print(f"Error synthesizing responses: {str(e)}")
        # Fall back to the AI response if synthesis fails
        return ai_response

def answer_query(query, selected_file=None):
    """
    Answer a user query by searching in all document files or a specific file.
    
    Args:
        query (str): User query
        selected_file (str, optional): If provided, search only in this file
        
    Returns:
        dict: Response containing the exact match, AI response, enhanced response, and file options
    """
    print(f"answer_query called with query='{query}', selected_file='{selected_file}'")
    
    if not query or len(query.strip()) == 0:
        print("Empty query received")
        return {
            "exact_match": "Please provide a specific query about Gujarat Civil Services.",
            "ai_response": "Please provide a specific query about Gujarat Civil Services.",
            "enhanced_response": "Please provide a specific query about Gujarat Civil Services.",
            "file_options": []
        }
    
    try:
        # Get exact match from the text and file options
        exact_match, file_options = find_relevant_text(query, documents, selected_file)
        print(f"find_relevant_text returned match of length {len(exact_match)} and {len(file_options)} file options")
        
        # If multiple file options and no file selected, return options for user to choose
        if len(file_options) > 1 and not selected_file:
            print(f"Multiple file options found: {file_options}")
            file_options_with_names = []
            for file_id in file_options:
                # Use a nicer display name for the file
                display_name = file_id.replace('_', ' ')
                file_options_with_names.append({"id": file_id, "name": display_name})
                
            return {
                "exact_match": exact_match,
                "ai_response": "Please select a document to continue.",
                "enhanced_response": "I found information in multiple documents. Please select which one you'd like me to use:",
                "file_options": file_options_with_names
            }
        
        # Get file ID if available
        file_id = file_options[0] if file_options else None
        print(f"Using file_id: {file_id}")
        
        # Get AI-generated response
        ai_response = get_ai_response(query, exact_match, file_id)
        print(f"Generated AI response of length {len(ai_response)}")
        
        # Generate enhanced response using RAG synthesis
        enhanced_response = get_enhanced_response(query, exact_match, ai_response, file_id)
        print(f"Generated enhanced response of length {len(enhanced_response)}")
        
        response_dict = {
            "exact_match": exact_match,
            "ai_response": ai_response,
            "enhanced_response": enhanced_response,
            "file_options": []  # Empty if no options needed
        }
        print(f"Returning response with keys: {list(response_dict.keys())}")
        return response_dict
    except Exception as e:
        print(f"Exception in answer_query: {e}")
        import traceback
        print(traceback.format_exc())
        
        # Return a default response in case of error
        return {
            "exact_match": f"Error processing query: {str(e)}",
            "ai_response": f"Error processing query: {str(e)}",
            "enhanced_response": f"I encountered an error while processing your query: {str(e)}",
            "file_options": []
        }

@app.on_event("startup")
async def startup_event():
    """Load all document files on startup"""
    global documents
    
    documents = load_data_files()
    print(f"Loaded {len(documents)} document files and ready for queries")

@app.post("/api/test")
async def test_endpoint(request: dict):
    """Simple test endpoint that echoes back the request data"""
    print(f"Received test request: {request}")
    return {"received": request}

@app.post("/api/query")
async def handle_query(request: dict):
    """Handle a query from the frontend - using dict for flexibility"""
    global documents
    
    print(f"Received raw query request: {request}")
    
    # Extract query and selected_file from request
    query = request.get("query", "")
    selected_file = request.get("selected_file", None)
    
    print(f"Extracted query: {query}")
    print(f"Extracted selected_file: {selected_file}")
    
    # Basic validation
    if not query or not isinstance(query, str) or query.strip() == "":
        return {
            "exact_match": "Please provide a specific query about Gujarat Civil Services.",
            "ai_response": "Please provide a specific query about Gujarat Civil Services.",
            "enhanced_response": "Please provide a specific query about Gujarat Civil Services.",
            "response": "Please provide a specific query about Gujarat Civil Services.",
            "file_options": []
        }
    
    # Clean the query string
    query = query.strip()
    
    if not documents:
        print("No documents loaded, attempting to load...")
        documents = load_data_files()
        if not documents:
            print("Failed to load documents")
            return {
                "exact_match": "The document data is not available.",
                "ai_response": "The document data is not available.",
                "enhanced_response": "The document data is not available.",
                "response": "The document data is not available.",
                "file_options": []
            }
    
    try:
        print(f"Processing query with {len(documents)} loaded documents")
        result = answer_query(query, selected_file)
        
        # Return the result for the frontend display
        response = {
            "exact_match": result.get("exact_match", "No direct match found."),
            "ai_response": result.get("ai_response", "No AI response available."),
            "enhanced_response": result.get("enhanced_response", "No enhanced response available."),
            "response": result.get("enhanced_response", "No response available."),
            "file_options": result.get("file_options", [])
        }
        print(f"Sending response: {response}")
        return response
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(error_msg)
        print(f"Error details: {type(e).__name__}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        
        # Return a graceful error response instead of raising an exception
        return {
            "exact_match": "An error occurred while processing your query.",
            "ai_response": "An error occurred while processing your query.",
            "enhanced_response": f"I'm sorry, there was an error processing your query: {str(e)}",
            "response": f"I'm sorry, there was an error processing your query: {str(e)}",
            "file_options": []
        }

@app.post("/api/chatbot", response_model=dict)
async def legacy_handle_query(request: dict):
    """Handle a query from older versions of the frontend"""
    if not request or "query" not in request:
        return {"response": "Please provide a query about Gujarat Civil Services."}
    
    try:
        # Convert to the new format
        selected_file = request.get("selected_file", None)
        new_request = QueryRequest(query=request["query"], selected_file=selected_file)
        
        # Process using the new handler
        result = await handle_query(new_request)
        
        # Return in the old format - prioritize enhanced response
        return {
            "response": result.enhanced_response or result.response,
            "file_options": result.file_options
        }
    except Exception as e:
        print(f"Error processing legacy query: {str(e)}")
        return {"response": "I'm having trouble processing your query. Please try again."}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Gujarat Civil Services Chatbot API is running"}

def main():
    """
    Main function to start the chatbot API server.
    """
    import uvicorn
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8002)

if __name__ == "__main__":
    main() 