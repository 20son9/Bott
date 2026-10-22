import os, pickle, faiss, numpy as np
from sentence_transformers import SentenceTransformer
from ingest import process_all_books
from chunk import chunk_pages

def build_index(books_dir, index_dir):
    print("Extracting text...")
    pages = process_all_books(books_dir)
    chunks = chunk_pages(pages)
    print(f"Created {len(chunks)} chunks.")
    
    print("Loading model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    print("Embedding...")
    texts = [c["text"] for c in chunks]
    embeddings = np.array(model.encode(texts)).astype('float32')
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    os.makedirs(index_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(index_dir, "faiss_index.bin"))
    with open(os.path.join(index_dir, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)
    print("Index built successfully!")

if __name__ == "__main__":
    build_index("data/books", "artifacts")
