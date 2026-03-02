# src/llm/rerank.py
from __future__ import annotations

import json
import re
from openai import OpenAI
from src.config import RERANK_MODEL

client = OpenAI()

def _compact_candidate(r: dict) -> dict:
    return {
        "rank": r.get("rank"),
        "doc_id": r.get("doc_id"),
        "chunk_id": r.get("chunk_id"),
        "title": r.get("title"),
        "source": r.get("source"),
        "date": r.get("date"),
        "ticker": r.get("ticker"),
        "text": (r.get("text_preview") or r.get("text") or "")[:600],
    }

def llm_rerank_top1(query: str, candidates: list[dict], model: str = RERANK_MODEL) -> int:
    """
    Returns: chosen_index (0-based) among candidates
    """
    if not candidates:
        return 0

    payload = {"query": query, "candidates": [_compact_candidate(r) for r in candidates]}

    system = (
        "You are a retrieval reranker for an investment RAG system. "
        "Pick the SINGLE candidate that most directly answers the query with explicit evidence. "
        "Prefer specificity and direct match to the query constraints. "
        "Return ONLY JSON: {\"best_rank\": <rank_number_from_candidates>}."
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=0
    )

    text = (resp.choices[0].message.content or "").strip()
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return 0

    obj = json.loads(m.group(0))
    best_rank = int(obj.get("best_rank", candidates[0].get("rank", 1)))

    for i, r in enumerate(candidates):
        if int(r.get("rank", -1)) == best_rank:
            return i
    return 0

def promote_chosen_to_top(candidates: list[dict], chosen_i: int) -> list[dict]:
    chosen = candidates[chosen_i]
    rest = [r for j, r in enumerate(candidates) if j != chosen_i]
    reranked = [chosen] + rest
    for i, r in enumerate(reranked, start=1):
        r["rank"] = i
    return reranked