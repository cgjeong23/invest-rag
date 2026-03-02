# src/eval/search_wrappers.py
from __future__ import annotations

from typing import Callable, List, Dict, Any, Optional
import numpy as np

from src.retrieval.vector_store import VectorStore, l2_normalize
from src.llm.rerank import llm_rerank_top1, promote_chosen_to_top

EmbedQueryFn = Callable[[str], np.ndarray]                 # returns (d,) or (1,d)
SearchFn = Callable[[str, int], List[Dict[str, Any]]]      # query, k -> ranked results


def _ensure_2d_float32(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32)
    if v.ndim == 1:
        v = v[None, :]
    if v.ndim != 2 or v.shape[0] != 1:
        raise ValueError(f"Expected query vector shape (1,d) or (d,), got {v.shape}")
    return v


def make_vectorstore_search_fn(
    vs: VectorStore,
    *,
    embed_query: EmbedQueryFn,
    normalize: bool = True,
) -> SearchFn:
    """Text query -> embedding -> (optional) normalize -> VectorStore search."""
    def search_fn(query: str, k: int) -> List[Dict[str, Any]]:
        query = (query or "").strip()
        if not query:
            return []
        qv = _ensure_2d_float32(embed_query(query))
        if normalize:
            qv = l2_normalize(qv)
        return vs.search_by_vector(qv, k=k)
    return search_fn


def make_llm_rerank_search_fn(
    base_search_fn: SearchFn,
    *,
    k_vec: int = 10,
    rerank_model: Optional[str] = None,
) -> SearchFn:
    """
    LLM rerank wrapper.
    - Pick candidate based on base_search_fn(query, k_vec)
    - Rerank candidate with llm_rerank_top1
    - Return Final topK
    """
    def search_fn(query: str, k: int) -> List[Dict[str, Any]]:
        candidates = base_search_fn(query, k_vec)
        if not candidates:
            return []

        if rerank_model is None:
            chosen_i = llm_rerank_top1(query, candidates)
        else:
            chosen_i = llm_rerank_top1(query, candidates, model=rerank_model)

        reranked = promote_chosen_to_top(candidates, chosen_i)
        return reranked[:k]

    return search_fn