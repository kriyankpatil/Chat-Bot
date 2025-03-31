"""
Text extraction module for handling unstructured data sources.
"""
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PyPDF2 not installed - PDF extraction disabled")

try:
    import pytesseract
    from PIL import Image
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False
    print("pytesseract or PIL not installed - OCR extraction disabled")

class TextExtractor:
    """
    Class to extract text from various unstructured data sources
    such as PDFs, images, and text files.
    """
    
    @staticmethod
    def extract_from_pdf(file_path):
        """
        Extract text from a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text
        """
        if not PDF_SUPPORT:
            print("PDF extraction is not available. Install PyPDF2")
            return "PDF extraction is not available. Install PyPDF2"
            
        try:
            print(f"Attempting to read PDF from: {file_path}")
            reader = PdfReader(file_path)
            text = ""
            page_count = len(reader.pages)
            print(f"PDF has {page_count} pages")
            
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    text += page_text + "\n\n"
                    print(f"Extracted page {i+1}/{page_count} with {len(page_text)} characters")
                except Exception as e:
                    print(f"Error extracting text from page {i+1}: {e}")
            
            if not text.strip():
                print("Warning: No text was extracted from the PDF")
                return "The PDF appears to be empty or contain only images. No text was extracted."
                
            return text
        except Exception as e:
            error_message = f"Error extracting text from PDF: {str(e)}"
            print(error_message)
            return error_message
    
    @staticmethod
    def extract_from_image(file_path):
        """
        Extract text from an image using OCR.
        
        Args:
            file_path (str): Path to the image file
            
        Returns:
            str: Extracted text
        """
        if not OCR_SUPPORT:
            print("OCR extraction is not available. Install pytesseract and Pillow")
            return "OCR extraction is not available. Install pytesseract and Pillow"
            
        try:
            print(f"Attempting to extract text from image: {file_path}")
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            print(f"Extracted {len(text)} characters from image")
            return text
        except Exception as e:
            error_message = f"Error extracting text from image: {str(e)}"
            print(error_message)
            return error_message
    
    @staticmethod
    def extract_from_text_file(file_path):
        """
        Extract text from a plain text file.
        
        Args:
            file_path (str): Path to the text file
            
        Returns:
            str: Extracted text
        """
        try:
            print(f"Reading text file: {file_path}")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
                print(f"Read {len(text)} characters from text file")
                return text
        except Exception as e:
            error_message = f"Error reading text file: {str(e)}"
            print(error_message)
            return error_message 