# Rule-Based Chatbot Backend

A backend system for a rule-based chatbot that extracts, processes, and structures unstructured text data to answer user queries about organizational rules and policies.

## Features

- **Text Extraction**: Extract text from various unstructured data sources (PDFs, images, text files)
- **Text Preprocessing**: Clean, normalize, and prepare text for analysis
- **Text Structuring**: Organize unstructured text into structured formats (JSON, CSV)
- **Rule Matching**: Match user queries with relevant rules using keyword and pattern matching

## Project Structure

```
├── app/
│   ├── data/                  # Directory for input data and processed rules
│   ├── modules/               # Core functionality modules
│   │   ├── text_extractor.py  # Text extraction from different sources
│   │   ├── text_preprocessor.py  # Text preprocessing and normalization
│   │   ├── text_structurer.py # Text structuring and formatting
│   │   └── rule_matcher.py    # Rule matching logic
│   ├── utils/                 # Utility functions
│   └── main.py                # Main application entry point
└── requirements.txt           # Project dependencies
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Download spaCy model:
   ```
   python -m spacy download en_core_web_sm
   ```

## Usage

1. Place your unstructured data files (PDFs, images, text files) in the `app/data` directory
2. Run the main application:
   ```
   python -m app.main
   ```
3. The application will:
   - Extract text from the data files
   - Preprocess the extracted text
   - Structure the text into rules
   - Save the rules to a JSON file
   - Initialize a chatbot with the rules
   - Answer sample queries

## Requirements

- Python 3.8+
- PyPDF2
- spaCy
- Tesseract OCR (for image text extraction)
- FastAPI (for future API development)

## Future Enhancements

- API endpoint for chatbot integration
- Advanced NLP techniques for better rule extraction
- Database integration for rule storage
- UI for managing rules and viewing analytics 