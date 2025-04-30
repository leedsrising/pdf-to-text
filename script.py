import os

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Input/output paths
pdf_path = "your_file.pdf"
output_text_path = "output.txt"
dpi = 300  # Higher DPI = better OCR accuracy

# Convert PDF to list of images
print("Converting PDF to images...")
images = convert_from_path(pdf_path, dpi=dpi)

# Extract text from each page
print("Running OCR...")
all_text = []
for i, img in enumerate(images):
    text = pytesseract.image_to_string(img)
    all_text.append(f"--- Page {i+1} ---\n{text}\n")

# Save the full text
with open(output_text_path, "w", encoding="utf-8") as f:
    f.writelines(all_text)

print(f"Done. OCR text saved to {output_text_path}")