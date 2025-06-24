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
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 15)
    return adaptive

def run_easyocr(image):
    result = easy_reader.readtext(image)
    return "\n".join([item[1] for item in result])

def run_tesseract(image):
    custom_config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(image, config=custom_config)

def extract_fields(text):
    fields = {
        "Invoice Number": None,
        "GSTINs": []
    }

    invoice_keywords = [
        "invoice no", "invoice number", "inv no", "inv.", "inv#", "doc no", "document no",
        "bill no", "reference no", "ref no", "ref:", "invoice:", "inv:"  # expanded
    ]

    false_hits = {"PRIVATE", "ORIGINAL", "INVOICE", "COPY", "TAX", "BILL", "SERVICE"}
    candidates = []

    lines = text.splitlines()
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw in line_lower for kw in invoice_keywords):
            match = re.search(r"([A-Z0-9\/\-\._]{6,25})", line, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if val.upper() not in false_hits:
                    candidates.append(val)
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                match_next = re.search(r"([A-Z0-9\/\-\._]{6,25})", next_line)
                if match_next:
                    val = match_next.group(1).strip()
                    if val.upper() not in false_hits:
                        candidates.append(val)

    for val in candidates:
        if re.search(r"\d", val):  # contains at least one digit
            fields["Invoice Number"] = val
            break

    if not fields["Invoice Number"] and candidates:
        fields["Invoice Number"] = max(candidates, key=len)

    gstin_matches = re.findall(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}\b", text)
    fields["GSTINs"] = list(set(gstin_matches))

    return fields

# === MAIN EXECUTION ===
file_path = r"C:\Users\manns\Desktop\OCR BW\SO25-26AWN046 (1).pdf"
image = load_pdf(file_path)
processed_image = preprocess_image(image)

# OCR
easyocr_text = run_easyocr(processed_image)
tesseract_text = run_tesseract(processed_image)
combined_text = easyocr_text + "\n" + tesseract_text

# Extract fields
fields = extract_fields(combined_text)

# Print extracted key fields
print("\n=== KEY EXTRACTED FIELDS ===\n")
for key, val in fields.items():
    if isinstance(val, list):
        print(f"{key}: {', '.join(val) if val else 'Not found'}")
    else:
        print(f"{key}: {val if val else 'Not found'}")
