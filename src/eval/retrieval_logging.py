# src/eval/retrieval_logging.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json


def log_retrieval(
    *,
    log_path: Path,
    query: str,
    results: list[dict],
    comment: str | None = None,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "query": query,
        "top_k": len(results),
        "results": [
            {
                "rank": r.get("rank"),
                "score": r.get("score"),
                "chunk_id": r.get("chunk_id"),
                "source": r.get("source"),
                "ticker": r.get("ticker"),
                "date": r.get("date"),
                "title": r.get("title"),
            }
            for r in results
        ],
        "comment": comment,
    }

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")