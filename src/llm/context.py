# src/llm/context.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from src.config import MAX_CHARS_PER_DOC, MAX_CONTEXT_CHARS
except Exception:
    MAX_CHARS_PER_DOC = 1400
    MAX_CONTEXT_CHARS = 8000


def _clean_text(x: str) -> str:
    # Change line / Erase space for LLM readability
    return " ".join((x or "").replace("\r", "\n").split())


def build_context(
    results: List[Dict[str, Any]],
    *,
    max_chars_per_doc: int = MAX_CHARS_PER_DOC,
    max_total_chars: int = MAX_CONTEXT_CHARS,
    require_doc_id: bool = True,
) -> str:
    """
    Build context string for generation.
    - Exposes doc_id clearly to support [doc_id] citations.
    - Skips items without doc_id by default (so citation validation stays clean).
    - Enforces per-item and total budget.
    """
    blocks: List[str] = []
    total = 0

    for r in results:
        doc_id = r.get("doc_id")
        if require_doc_id and not doc_id:
            # citation 정책이 [doc_id]라면 doc_id 없는 문서는 넣지 않는게 가장 깔끔
            continue

        raw = r.get("text") or r.get("text_preview") or ""
        text = _clean_text(raw)
        if not text:
            continue

        if len(text) > max_chars_per_doc:
            text = text[: max_chars_per_doc].rstrip() + "..."

        # 메타는 없는 필드도 많으니 안전하게
        date = (r.get("date") or "").strip()
        ticker = (r.get("ticker") or "").strip()
        source = (r.get("source") or "").strip()
        title = (r.get("title") or "").strip()

        # header: doc_id를 "대괄호"로 선명하게 (모델이 그대로 인용하기 쉬움)
        # 예: [AAPL_2024Q4_001]
        head_id = f"[{doc_id}]" if doc_id else "[source]"
        meta_parts = [p for p in [date, ticker, source] if p]
        meta_str = ", ".join(meta_parts)

        header = head_id
        if meta_str:
            header += f" ({meta_str})"
        if title:
            header += f" {title}"

        block = f"{header}\n{text}"

        add_len = len(block) + 2
        if total + add_len > max_total_chars:
            break

        blocks.append(block)
        total += add_len

    return "\n\n".join(blocks)