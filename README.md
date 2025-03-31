# Rule-Based Expert System Chatbot

A comprehensive rule-based expert system chatbot designed to assist users in understanding organizational policies and procedures. This project consists of both a modern frontend UI and a robust backend for extracting, processing, and structuring unstructured text data.

## Features

### Frontend (UI)
- Modern, responsive chat interface
- File upload capability
- Chat history sidebar
- Profile icon and menu
- Rule-based response system
- Markdown support for bot responses

### Backend
- Extracts text from unstructured data (PDFs, images, text files)
- Cleans, normalizes, and structures text into a readable format
- Matches user queries with relevant rules using keyword and pattern matching

## Technologies Used

### Frontend
- React
- TypeScript
- Tailwind CSS
- Heroicons
- React Markdown

### Backend
- Python 3.8+
- FastAPI (for future API development)
- PyPDF2 (for PDF text extraction)
- spaCy (for NLP processing)
- Tesseract OCR (for image text extraction)

## Getting Started

### Prerequisites
#### Frontend:
- Node.js (v14 or later)
- npm or yarn

#### Backend:
- Python 3.8+
- Required dependencies (see `requirements.txt`)

### Installation
#### Frontend:
1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm start
   ```
5. Open [http://localhost:3000](http://localhost:3000) in a browser

#### Backend:
1. Clone the repository
2. Navigate to the backend directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
5. Run the main application:
   ```bash
   python -m app.main
   ```

## Project Structure

### Frontend
```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── ChatContainer.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
```

### Backend
```
backend/
├── app/
│   ├── data/                  # Input data and processed rules
│   ├── modules/               # Core functionality
│   │   ├── text_extractor.py  # Text extraction
│   │   ├── text_preprocessor.py  # Text cleaning and normalization
│   │   ├── text_structurer.py # Text structuring
│   │   ├── rule_matcher.py    # Rule matching
│   ├── utils/                 # Utility functions
│   └── main.py                # Entry point
└── requirements.txt           # Dependencies
```

## Customization
To modify the chatbot’s rule-based responses:
- **Frontend:** Edit the `generateBotResponse` function in `App.tsx`.
- **Backend:** Update `rule_matcher.py` to refine rule-matching logic.

## Future Enhancements
- API endpoint for chatbot integration
- Advanced NLP techniques for improved rule extraction
- Database integration for rule storage
- UI for rule management and analytics

