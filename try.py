import os
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import easyocr
import re

# Initialize OCR engines
easy_reader = easyocr.Reader(['en'])
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def load_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    image_formats = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

    if ext == ".pdf":
        images = convert_from_path(file_path)
        image = np.array(images[0])
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    elif ext in image_formats:
        image = cv2.imread(file_path)
        if image is None:
            raise FileNotFoundError(f"Cannot open image: {file_path}")
    else:
        raise ValueError("Unsupported file format. Use PDF or image (.jpg/.png/.bmp/etc).")

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

    # Fuzzy pattern for common invoice/document formats
    doc_match = re.search(r"(INV[-/]?\d{4,6}|#\d{3,6}|[A-Z]{2,4}-\d{3,5})", text, re.IGNORECASE)
    if doc_match:
        fields["Document Number"] = doc_match.group()

    # Relaxed pattern to capture GSTINs with potential OCR distortions
    gstin_matches = re.findall(r"\b\d{2}[A-Z0-9]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b", text)
    fields["GSTINs"] = list(set(gstin_matches))

    return fields

# === RUN THE OCR ===
file_path = r"C:\Users\manns\Downloads\invoice_10.pdf0.jpg" # Change to your file
image = load_file(file_path)
processed_image = preprocess_image(image)

# Run EasyOCR
easyocr_text = run_easyocr(processed_image)

# Run Tesseract
tesseract_text = run_tesseract(processed_image)

# Combine texts
combined_text = easyocr_text + "\n" + tesseract_text

# Print raw OCR output
print("\n📝 === RAW OCR TEXT (EasyOCR + Tesseract) ===\n")
print(combined_text)

# Extract and print fields
print("\n📌 === KEY EXTRACTED FIELDS ===\n")
fields = extract_fields(combined_text)
for key, val in fields.items():
    if isinstance(val, list):
        print(f"{key}: {', '.join(val) if val else 'Not found'}")
    else:
        print(f"{key}: {val if val else 'Not found'}")

# Debug: Print lines that may contain GSTINs
print("\n🔎 === GSTIN LINES FROM TEXT (for debugging) ===\n")
for line in combined_text.splitlines():
    if "GST" in line.upper():
        print("🔍", line)

