import os
from pathlib import Path
from typing import Dict, List, Tuple

import fitz  # PyMuPDF
from dotenv import load_dotenv


class PDFExtractor:
    def __init__(self, output_dir: str = 'text_output'):
        """Initialize the PDF extractor with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_text_with_layout(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF while preserving layout information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing text blocks with layout information
        """
        try:
            doc = fitz.open(pdf_path)
            all_text = []
            
            for page_num, page in enumerate(doc):
                # Get text blocks with their positions
                blocks = page.get_text("dict")["blocks"]
                
                # Process each block
                for block in blocks:
                    if "lines" in block:  # Text block
                        block_text = []
                        for line in block["lines"]:
                            line_text = []
                            for span in line["spans"]:
                                # Get text and its position
                                text = span["text"]
                                bbox = span["bbox"]  # (x0, y0, x1, y1)
                                font = span["font"]
                                size = span["size"]
                                
                                # Store text with its layout info
                                line_text.append({
                                    "text": text,
                                    "bbox": bbox,
                                    "font": font,
                                    "size": size
                                })
                            block_text.append(line_text)
                        
                        # Add block text with position info
                        all_text.append({
                            "page": page_num + 1,
                            "block": block_text,
                            "bbox": block["bbox"]
                        })
            
            return all_text
            
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {str(e)}")
            return []
        finally:
            if 'doc' in locals():
                doc.close()
    
    def save_text_with_layout(self, text_data: List[Dict], output_path: str):
        """
        Save extracted text with layout information to a structured format.
        
        Args:
            text_data: List of text blocks with layout information
            output_path: Path to save the output file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for block in text_data:
                    f.write(f"--- Page {block['page']} ---\n")
                    for line in block["block"]:
                        for span in line:
                            # Write text with its position info
                            f.write(f"{span['text']} [pos:{span['bbox']}, font:{span['font']}, size:{span['size']}]\n")
                    f.write("\n")
        except Exception as e:
            print(f"Error saving text to {output_path}: {str(e)}")
    
    def process_pdf(self, pdf_path: str):
        """
        Process a single PDF file and save its text with layout information.
        
        Args:
            pdf_path: Path to the PDF file
        """
        try:
            output_path = self.output_dir / f"{Path(pdf_path).stem}_layout.txt"
            
            print(f"Processing {pdf_path}...")
            text_data = self.extract_text_with_layout(pdf_path)
            
            if text_data:
                self.save_text_with_layout(text_data, output_path)
                print(f"Saved layout-preserved text to {output_path}")
            else:
                print(f"No text data extracted from {pdf_path}")
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")

def main():
    """Main function to process PDF files from environment variable."""
    # Load environment variables
    load_dotenv()
    
    # Get PDF files from environment variable
    pdf_files = os.getenv('PDF_FILES', '').split(',')
    
    if not pdf_files or not pdf_files[0]:
        print("No PDF files specified in PDF_FILES environment variable")
        return
    
    extractor = PDFExtractor()
    
    for pdf_path in pdf_files:
        pdf_path = pdf_path.strip()
        if os.path.exists(pdf_path):
            extractor.process_pdf(pdf_path)
        else:
            print(f"Warning: PDF file not found: {pdf_path}")

if __name__ == "__main__":
    main() 