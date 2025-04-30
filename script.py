import os

import pytesseract
from dotenv import load_dotenv
from pdf2image import convert_from_path
from PIL import Image

# Load environment variables
load_dotenv()

# Get PDF files from environment variable
pdf_files = os.getenv('PDF_FILES').split(',') if os.getenv('PDF_FILES') else []

# OCR settings
dpi = 300  # Higher DPI = better OCR accuracy

# Create output directory for text files
output_dir = 'text_output'
os.makedirs(output_dir, exist_ok=True)

def process_pdf(pdf_path):
    # Create output filename based on input PDF name
    output_text_path = os.path.join(output_dir, os.path.splitext(os.path.basename(pdf_path))[0] + '.txt')
    
    # Convert PDF to list of images
    print(f"Converting {pdf_path} to images...")
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

def main():
    if not pdf_files:
        print("No PDF files found in PDF_FILES environment variable")
        return

    for pdf_path in pdf_files:
        pdf_path = pdf_path.strip()  # Remove any whitespace
        if os.path.exists(pdf_path):
            process_pdf(pdf_path)
        else:
            print(f"Warning: PDF file not found: {pdf_path}")

if __name__ == "__main__":
    main()