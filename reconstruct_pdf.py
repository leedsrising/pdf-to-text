import re
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

# Path to the layout-preserved text file
LAYOUT_FILE = 'text_output/post_ic_memo_layout.txt'
OUTPUT_PDF = 'text_output/post_ic_memo_reconstructed.pdf'

# Default page size (letter)
PAGE_WIDTH, PAGE_HEIGHT = letter

# Built-in fonts available in reportlab
BUILTIN_FONTS = {'Helvetica', 'Times-Roman', 'Courier'}
DEFAULT_FONT = 'Helvetica'

# Regex to parse lines like: Text [pos:(x0,y0,x1,y1), font:fontname, size:12]
LINE_RE = re.compile(r'^(.*) +\[pos:\(([-\d.]+),([-\d.]+),([-\d.]+),([-\d.]+)\), font:([^,]+), size:([\d.]+)\]\s*$')
PAGE_HEADER_RE = re.compile(r'^--- Page (\d+) ---$')


def parse_layout_file(layout_path):
    # Print the first 10 lines for debugging
    with open(layout_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print("First 10 lines of layout file:")
    for l in lines[:10]:
        print(repr(l.rstrip('\n')))
    # Now parse as before
    pages = []
    current_page = []
    no_match_count = 0
    for line in lines:
        line = line.rstrip('\n')
        page_header = PAGE_HEADER_RE.match(line)
        if page_header:
            if current_page:
                pages.append(current_page)
            current_page = []
        elif line.strip() == '':
            continue
        elif '[pos:' in line:
            text, meta = line.split('[pos:', 1)
            text = text.rstrip()
            meta = meta.rstrip('] \n')
            # Now parse meta for coordinates, font, size
            m = LINE_RE.match(meta)
            if m:
                x0 = float(m.group(2))
                y0 = float(m.group(3))
                x1 = float(m.group(4))
                y1 = float(m.group(5))
                font = m.group(6)
                size = float(m.group(7))
                current_page.append({
                    'text': text,
                    'x0': x0,
                    'y0': y0,
                    'x1': x1,
                    'y1': y1,
                    'font': font,
                    'size': size
                })
            else:
                if no_match_count < 10:
                    print(f"NO MATCH: {repr(line)}")
                no_match_count += 1
    if no_match_count > 10:
        print(f"...and {no_match_count - 10} more NO MATCH lines suppressed.")
    if current_page:
        pages.append(current_page)
    return pages


def reconstruct_pdf(layout_path, output_pdf):
    pages = parse_layout_file(layout_path)
    print(f"Parsed {len(pages)} pages from layout file.")
    for i, page in enumerate(pages):
        print(f"Page {i+1}: {len(page)} text items.")
        if i == 0 and page:
            xs = [item['x0'] for item in page] + [item['x1'] for item in page]
            ys = [item['y0'] for item in page] + [item['y1'] for item in page]
            print(f"  x range: {min(xs)} to {max(xs)}")
            print(f"  y range: {min(ys)} to {max(ys)}")
    c = canvas.Canvas(output_pdf, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for page in pages:
        if not page:
            continue  # skip empty pages
        for item in page:
            # Use built-in font if available, otherwise fallback
            font_name = item['font'] if item['font'] in BUILTIN_FONTS else DEFAULT_FONT
            c.setFont(font_name, item['size'])
            # Place text at (x0, PAGE_HEIGHT - y0) to align with the text baseline
            x = item['x0']
            y = PAGE_HEIGHT - item['y0']
            c.drawString(x, y, item['text'])
        c.showPage()
    c.save()
    print(f"Reconstructed PDF saved to {output_pdf}")


def main():
    if not Path(LAYOUT_FILE).exists():
        print(f"Layout file not found: {LAYOUT_FILE}")
        return
    reconstruct_pdf(LAYOUT_FILE, OUTPUT_PDF)

if __name__ == "__main__":
    main() 