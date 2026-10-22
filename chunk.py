def chunk_pages(pages, chunk_size=500, overlap=50):
    chunks = []
    for page in pages:
        text = page["text"]
        start = 0
        chunk_num = 1
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "group_id": "G020",
                "subject": "Computer Science",
                "book_id": page["book_id"],
                "title": "Pending",
                "edition": "1st",
                "page": page["page"],
                "chunk_id": f"{page['book_id']}_P{page['page']}_C{chunk_num:02d}",
                "text": chunk_text
            })
            start += (chunk_size - overlap)
            chunk_num += 1
    return chunks
