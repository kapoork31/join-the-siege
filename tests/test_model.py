import pytest
from io import BytesIO
from PIL import Image
from src.utils.extract_text import PDFTextExtractor, TxtTextExtractor, OCRTextExtractor
from src.classifier import classify_file_ml

# Path to sample test files (you need to create these files in your testing environment)
PDF_FILE_PATH = 'files/bank_statement_1.pdf'
JPG_FILE_PATH = 'files/drivers_license_1.jpg'

# Test text extraction from PDF
def test_pdf_text_extractor():
    with open(PDF_FILE_PATH, 'rb') as f:
        file_bytes = BytesIO(f.read())
        extractor = PDFTextExtractor()
        text = extractor.extract_text(file_bytes)
        assert "Statement" in text  # Adjust this to match the content in your test PDF

# Test text extraction from JPG using OCR
def test_ocr_text_extractor():
    with open(JPG_FILE_PATH, 'rb') as f:
        file_bytes = BytesIO(f.read())
        extractor = OCRTextExtractor()
        text = extractor.extract_text(file_bytes)
        assert "LICENSE" in text  # Assuming "sample" text exists in the test image (adjust accordingly)

# Test the text classification (this assumes you have a valid classifier model already trained)
def test_classify_invoice():
    text = "Invoice Number: 1234 Date: 15 December 2023 Item: Design $50"
    result = classify_file_ml(text)
    assert result == 'invoice'

def test_classify_bank_statement():
    text = "Account Holder: John Doe 1 Account Number: XXXX-XXXX-XXXX-6781 Statement Period: 2023-01, Direct Deposit"
    result = classify_file_ml(text)
    assert result == 'bank_statement'

def test_classify_drivers_license():
    text = "ANY STATE DRIVER LICENSE License No. P99999999 Expires 00-00-00 JOE A SAMPLE"
    result = classify_file_ml(text)
    assert result == 'driver_license'

if __name__ == "__main__":
    pytest.main()
