import os
import json
import fitz

def generate_manifest(books_dir, output_file):
    manifest = []
    if not os.path.exists(books_dir):
        print(f"Error: Folder {books_dir} not found.")
        return

    pdf_files = [f for f in os.listdir(books_dir) if f.endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDFs. Processing...")

    for idx, filename in enumerate(pdf_files):
        book_id = f"G020_BOOK_{idx+1:03d}"
        pdf_path = os.path.join(books_dir, filename)
        
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            
            manifest.append({
                "book_id": book_id,
                "title": filename.replace(".pdf", "").replace("_", " ").title(), # Auto-fill title
                "author": "REPLACE_WITH_AUTHOR", 
                "edition": "1st",
                "publisher": "REPLACE_WITH_PUBLISHER",
                "year": "2024",
                "ISBN": "REPLACE_WITH_ISBN",
                "subject": "Computer Science",
                "source_type": "PDF text",
                "permission_status": "Open Access / Educational Use",
                "processing_status": "Pending",
                "page_count": page_count,
                "filename": filename
            })
            print(f"Added {filename} ({page_count} pages) as {book_id}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"\nSuccess! Created {output_file}")
    print("IMPORTANT: Open data/book_manifest.json and replace all 'REPLACE_WITH...' fields.")

if __name__ == "__main__":
    generate_manifest("data/books", "data/book_manifest.json")