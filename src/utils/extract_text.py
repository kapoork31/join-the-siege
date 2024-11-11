import easyocr
import PyPDF2
from docx import Document
from PIL import Image
from io import BytesIO
import os

# Factory Base class for extracting text from different file types. 
# Each Subclasses should override the `extract_text` method for respetive file format
class TextExtractor:
    def extract_text(self, file_bytes: BytesIO) -> str:
        """Extract text from the file bytes. This method should be overridden by subclasses."""
        raise NotImplementedError("Subclasses should implement this method.")

class PDFTextExtractor(TextExtractor):
    def extract_text(self, file_bytes: BytesIO) -> str:
        """Extract text from a PDF file."""
        text = ""
        pdf_reader = PyPDF2.PdfReader(file_bytes)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

class DocxTextExtractor(TextExtractor):
    def extract_text(self, file_bytes: BytesIO) -> str:
        """Extract text from a DOCX file."""
        file_bytes.seek(0)
        doc = Document(file_bytes)
        return "\n".join([para.text for para in doc.paragraphs])

class OCRTextExtractor(TextExtractor):
    def extract_text(self, file_bytes: BytesIO) -> str:
        """Extract text from an image file using OCR."""
        reader = easyocr.Reader(['en'])
        image = Image.open(file_bytes)  # Open the image from bytes
        result = reader.readtext(image)  # Perform OCR

        # Extract the text from the OCR result
        text = " ".join([item[1] for item in result])
        return text

class TxtTextExtractor(TextExtractor):
    def extract_text(self, file_bytes: BytesIO) -> str:
        """Extract text from a TXT file."""
        file_bytes.seek(0)  # Ensure we're at the beginning of the file
        text = file_bytes.read().decode('utf-8', errors='ignore')  # Decode the bytes to a string
        return text

def get_text_extractor(filename: str) -> TextExtractor:
    """Return the appropriate TextExtractor based on file extension."""

    _, file_extension = os.path.splitext(filename)
    if file_extension.lower() == '.pdf':
        return PDFTextExtractor()
    elif file_extension.lower() == '.docx':
        return DocxTextExtractor()
    elif file_extension.lower() == '.txt':
        return TxtTextExtractor()
    elif file_extension in {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}:
        return OCRTextExtractor()
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

# Usage Example
def extract_text_from_file(file_bytes: BytesIO, file_extension: str) -> str:
    """Extracts text from a file based on its extension using the appropriate extractor."""
    extractor = get_text_extractor(file_extension)
    return extractor.extract_text(file_bytes)