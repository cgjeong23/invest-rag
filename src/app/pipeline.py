# src/app/pipeline.py
from __future__ import annotations

from src.config import USE_RERANK_DEFAULT, K_VEC, K_CTX, RERANK_MODEL
from src.retrieval.vector_store import VectorStore
from src.llm.rerank import llm_rerank_top1, promote_chosen_to_top
from src.llm.context import build_context
from src.llm.generate import rag_generate_with_retry

_STORE: VectorStore | None = None

def get_store() -> VectorStore:
    global _STORE
    if _STORE is None:
        _STORE = VectorStore.load()
    return _STORE

def retrieve(query: str, use_rerank: bool = USE_RERANK_DEFAULT, k_vec: int = K_VEC, k_ctx: int = K_CTX) -> list[dict]:
    store = get_store()
    if not use_rerank:
        return store.search(query, k=k_ctx)

    # rerank: vector top-k_vec -> LLM pick best -> promote
    cands = store.search(query, k=k_vec)
    if not cands:
        return []

    chosen_i = llm_rerank_top1(query, cands, model=RERANK_MODEL)
    reranked = promote_chosen_to_top(cands, chosen_i)
    return reranked[:k_ctx]

def answer(query: str, use_rerank: bool = USE_RERANK_DEFAULT) -> dict:
    retrieved = retrieve(query, use_rerank=use_rerank)
    ctx = build_context(retrieved)
    ans, grounded = rag_generate_with_retry(query, ctx, retrieved)
    return {
        "query": query,
        "use_rerank": use_rerank,
        "retrieved": retrieved,
        "answer": ans,
        "grounded": grounded,
    }