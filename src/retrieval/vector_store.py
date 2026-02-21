# src/retrieval/vector_store.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import faiss

from src.data_pipeline.io_utils import read_jsonl


def l2_normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.maximum(norms, eps)


@dataclass
class VectorStore:
    index: faiss.Index
    meta: list[dict]

    @classmethod
    def load(cls, index_path: Path, meta_path: Path) -> "VectorStore":
        index = faiss.read_index(str(index_path))
        meta = read_jsonl(meta_path)
        return cls(index=index, meta=meta)

    def search_by_vector(self, qv: np.ndarray, k: int = 5) -> list[dict]:
        scores, idxs = self.index.search(qv, k)
        out = []
        for rank, (i, s) in enumerate(zip(idxs[0], scores[0]), start=1):
            if i < 0:
                continue
            out.append({"rank": rank, "score": float(s), **self.meta[i]})
        return out