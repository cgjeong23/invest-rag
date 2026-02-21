# src/retrieval/chunk_loader.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.data_pipeline.io_utils import read_jsonl


@dataclass(frozen=True)
class ChunkLoadResult:
    texts: list[str]
    chunk_ids: list[str]
    metas: list[dict[str, Any]]
    n_loaded: int
    n_non_empty: int


def load_chunks_for_index(
    chunks_path: Path,
    *,
    sort_by_chunk_id: bool = True,
    drop_empty_texts: bool = True,
) -> ChunkLoadResult:
    rows = read_jsonl(chunks_path)
    if not rows:
        raise ValueError(f"No rows found: {chunks_path}")

    if sort_by_chunk_id:
        rows = sorted(rows, key=lambda r: str(r.get("chunk_id", "")))

    texts, chunk_ids, metas = [], [], []
    for r in rows:
        if "chunk_id" not in r or "text" not in r:
            raise KeyError("chunks.jsonl must contain at least {chunk_id, text} per row.")
        t = r.get("text", "")

        if drop_empty_texts and (not isinstance(t, str) or not t.strip()):
            continue

        texts.append(t)
        chunk_ids.append(r["chunk_id"])
        metas.append(r.get("metadata", {}))

    if not texts:
        raise ValueError("No non-empty texts after filtering.")

    return ChunkLoadResult(
        texts=texts,
        chunk_ids=chunk_ids,
        metas=metas,
        n_loaded=len(rows),
        n_non_empty=len(texts),
    )