import faiss, pickle, os, numpy as np
from sentence_transformers import SentenceTransformer

_index, _chunks, _model = None, None, None

def load_resources(index_dir="artifacts"):
    global _index, _chunks, _model
    if _index is None:
        _index = faiss.read_index(os.path.join(index_dir, "faiss_index.bin"))
        with open(os.path.join(index_dir, "chunks.pkl"), "rb") as f:
            _chunks = pickle.load(f)
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def retrieve(question: str, top_k: int = 5) -> list:
    load_resources()
    q_emb = _model.encode([question]).astype('float32')
    distances, indices = _index.search(q_emb, top_k)
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            c = _chunks[idx]
            results.append({"text": c["text"], "score": float(1/(1+distances[0][i])), 
                            "book_id": c["book_id"], "page": c["page"], "chunk_id": c["chunk_id"]})
    return results
