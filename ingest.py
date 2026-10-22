import fitz
import os

def extract_text_from_pdf(pdf_path, book_id):
    doc = fitz.open(pdf_path)
    pages_data = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            pages_data.append({"book_id": book_id, "page": page_num + 1, "text": text})
    doc.close()
    return pages_data

def process_all_books(books_dir):
    all_pages = []
    if not os.path.exists(books_dir): return []
    for idx, filename in enumerate(os.listdir(books_dir)):
        if filename.endswith(".pdf"):
            book_id = f"G020_BOOK_{idx+1:03d}"
            pages = extract_text_from_pdf(os.path.join(books_dir, filename), book_id)
            all_pages.extend(pages)
    return all_pages
