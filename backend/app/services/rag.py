import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL, INDEX_DIR

class KnowledgeBase:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index_path = os.path.join(INDEX_DIR, "revenue.faiss")
        self.meta_path = os.path.join(INDEX_DIR, "metadata.json")
        self.index = None
        self.metadata = []
        self._load()

    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

    def add_chunks(self, chunks, source):
        if not chunks:
            return 0
        vectors = self.model.encode(chunks, normalize_embeddings=True)
        vectors = np.asarray(vectors, dtype="float32")
        if self.index is None:
            self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        self.metadata.extend([{"text": c, "source": source} for c in chunks])
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        return len(chunks)

    def search(self, query, top_k=4):
        if self.index is None or not self.metadata:
            return []
        vector = self.model.encode([query], normalize_embeddings=True)
        scores, ids = self.index.search(np.asarray(vector, dtype="float32"), top_k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx >= 0:
                item = self.metadata[int(idx)].copy()
                item["score"] = float(score)
                results.append(item)
        return results
