## Overview

This document outlines the process for extracting text from PDFs while preserving their layout using PyMuPDF. The goal is to maintain the spatial relationships, formatting, and structure of the original PDF documents in the extracted text output.

## Goals

- Extract text from PDFs while preserving layout information
- Maintain spatial relationships between text elements
- Preserve font information and text sizes
- Support multi-column layouts and tables
- Generate structured output that can be used for document reconstruction

## Core Requirements

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install PyMuPDF==1.23.8 python-dotenv==1.1.0
```

### 2. Project Structure

```
pdf-to-text/
├── venv/
├── .env                    # Environment variables
├── pdf_extractor.py        # Main extraction script
├── text_output/           # Output directory
└── requirements.txt       # Project dependencies
```

### 3. Environment Variables

Create a `.env` file with:

```
PDF_FILES=path/to/pdf1.pdf,path/to/pdf2.pdf
```

### 4. Implementation Steps

1. **Create PDFExtractor Class**

   - Initialize with output directory
   - Handle PDF file opening and processing
   - Extract text with layout information
   - Save structured output

2. **Text Extraction Process**

   - Open PDF using PyMuPDF
   - Extract text blocks with positions
   - Preserve font information and sizes
   - Maintain page structure

3. **Output Format**
   - Save text with position coordinates
   - Include font and size information
   - Organize by pages and blocks
   - Use structured format for easy parsing

### 5. Usage

1. **Basic Usage**

```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor()
extractor.process_pdf("path/to/document.pdf")
```

2. **Command Line Usage**

```bash
# Set PDF_FILES environment variable
export PDF_FILES="path/to/pdf1.pdf,path/to/pdf2.pdf"

# Run the script
python pdf_extractor.py
```

### 6. Output Format Specification

The output file will contain:

```
--- Page 1 ---
Text content [pos:(x0,y0,x1,y1), font:fontname, size:12]
Next line [pos:(x0,y0,x1,y1), font:fontname, size:12]

--- Page 2 ---
...
```

Where:

- `pos:(x0,y0,x1,y1)` represents the text block's position
- `font:fontname` indicates the font used
- `size:12` shows the font size in points

### 7. Error Handling

The implementation should handle:

- Missing PDF files
- Corrupted PDFs
- Permission issues
- Invalid file paths
- Encoding problems

### 8. Performance Considerations

- Process PDFs page by page to manage memory
- Use efficient data structures for layout information
- Implement proper file handling and cleanup
- Consider batch processing for multiple files

## Reference Files

- `pdf_extractor.py` - Main implementation file
- `text_output/` - Directory for extracted text files
- `.env` - Environment configuration
- `requirements.txt` - Project dependencies

## Testing

1. **Basic Test Cases**

   - Single page PDF
   - Multi-page PDF
   - PDF with tables
   - PDF with multiple columns
   - PDF with different fonts and sizes

2. **Edge Cases**
   - Empty PDF
   - Corrupted PDF
   - PDF with images
   - PDF with complex layouts
   - Large PDF files

## Maintenance

1. **Regular Updates**

   - Keep PyMuPDF updated
   - Monitor for new PDF features
   - Update error handling as needed

2. **Documentation**
   - Update instructions for new features
   - Document any changes to output format
   - Maintain example files

## Security Considerations

1. **File Handling**

   - Validate input paths
   - Sanitize file names
   - Handle permissions properly

2. **Data Protection**
   - Secure storage of extracted text
   - Proper cleanup of temporary files
   - Access control for output files
