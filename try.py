import cv2
import pytesseract
from PIL import Image
import numpy as np
import os
from pdf2image import convert_from_path
import re

# Set up Tesseract path (modify if installed elsewhere)
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
    return Image.fromarray(inverted)

def extract_fields(text):
    fields = {
        "Invoice Number": None,
        "Date": None,
        "Total Amount": None
    }

    for line in text.split("\n"):
        line_clean = line.strip().lower()

        # Invoice Number
        if "invoice" in line_clean and ("no" in line_clean or "number" in line_clean):
            fields["Invoice Number"] = line.strip()

        # Date detection using common formats
        if "date" in line_clean:
            date_match = re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", line_clean)
            if date_match:
                fields["Date"] = date_match.group()

        # Total/Amount detection
        if "total" in line_clean or "amount" in line_clean:
            amt_match = re.search(r"\₹?\$?\d{1,3}(?:[,.\d]*)", line_clean)
            if amt_match:
                fields["Total Amount"] = amt_match.group()

    return fields

# === RUNNING THE OCR ===
file_path = r"C:\Users\manns\WhatsApp Image.pdf"  # ← Change to your file (image/pdf)
image = load_file(file_path)
processed_image = preprocess_image(image)
raw_text = pytesseract.image_to_string(processed_image, config="--psm 6")

# Print raw OCR text
print("\n📝 === RAW OCR TEXT ===\n")
print(raw_text)

# Extract and print key fields
print("\n📌 === KEY EXTRACTED FIELDS ===\n")
fields = extract_fields(raw_text)
for key, val in fields.items():
    print(f"{key}: {val if val else 'Not found'}")
