import fitz  # PyMuPDF

PDF_PATH = "confidential_data/post_ic_memo.pdf"  # Input PDF
OUTPUT_PATH = "confidential_data/post_ic_memo_replaced.pdf"  # Output PDF
SEARCH_TERM = "POST BROTHERS"  # Replace with the text you want to find
REPLACEMENT = "TEST"          # Replace with your desired replacement

def search_and_replace(pdf_path, output_path, search_term, replacement):
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc):
        # Find all instances of the search term (case-sensitive by default)
        found = page.search_for(search_term)
        for rect in found:
            # Redact (cover) the found text
            page.add_redact_annot(rect, fill=(1, 1, 1))  # White box
        page.apply_redactions()
        # Optionally, insert replacement text
        for rect in found:
            page.insert_textbox(rect, replacement, fontsize=10, color=(0, 0, 0), fontname="helv", align=1)
    doc.save(output_path)
    print(f"Saved replaced PDF to {output_path}")

if __name__ == "__main__":
    search_and_replace(PDF_PATH, OUTPUT_PATH, SEARCH_TERM, REPLACEMENT)