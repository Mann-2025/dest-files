import os
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract
import easyocr
import re

# Initialize OCR engines
easy_reader = easyocr.Reader(['en'])
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def load_pdf(file_path):
    images = convert_from_path(file_path)
    image = np.array(images[0])
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    inverted = cv2.bitwise_not(binary)
    return inverted

def run_easyocr(image):
    result = easy_reader.readtext(image)
    return "\n".join([item[1] for item in result])

def run_tesseract(image):
    return pytesseract.image_to_string(image)

def extract_fields(text):
    fields = {
        "Document Number": None,
        "GSTINs": []
    }

    # Enhanced patterns for various document/invoice number formats
    doc_patterns = [
        r"(Invoice\s*No\.?|Invoice\s*Number|INV\s*No\.?|Document\s*No\.?|Doc\s*No\.?|Bill\s*No\.?)\s*[:\-]?\s*([A-Z0-9#\/\-\.\_]{5,})",
        r"#\d{3,6}/[A-Z\-]{2,5}\d{2,4}",  # Fallback pattern
    ]

    for pattern in doc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields["Document Number"] = match.group(2) if len(match.groups()) > 1 else match.group(0)
            break

    # Pattern for GSTINs
    gstin_matches = re.findall(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}\b", text)
    fields["GSTINs"] = list(set(gstin_matches))

    return fields

# === MAIN EXECUTION ===
file_path = r"C:\Users\manns\Downloads\WhatsApp Image 2025-06-11 at 10.59.19 AM.pdf"  # Replace with your actual PDF path
image = load_pdf(file_path)
processed_image = preprocess_image(image)

# OCR
easyocr_text = run_easyocr(processed_image)
tesseract_text = run_tesseract(processed_image)
combined_text = easyocr_text + "\n" + tesseract_text

# Extract fields
fields = extract_fields(combined_text)

# Print extracted key fields
print("\n📌 === KEY EXTRACTED FIELDS ===\n")
for key, val in fields.items():
    if isinstance(val, list):
        print(f"{key}: {', '.join(val) if val else 'Not found'}")
    else:
        print(f"{key}: {val if val else 'Not found'}")
