# src/retrieval/artifacts.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
from datetime import datetime


def file_sha1(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


@dataclass(frozen=True)
class ChunksManifest:
    chunks_path: str
    line_count: int
    sha1: str
    sample_chunk_ids: list[str]


def build_chunks_manifest(chunks_path: Path, sample_n: int = 5) -> ChunksManifest:
    line_count = 0
    sample_chunk_ids: list[str] = []

    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            line_count += 1
            if len(sample_chunk_ids) < sample_n:
                try:
                    obj = json.loads(line)
                    cid = obj.get("chunk_id")
                    if cid:
                        sample_chunk_ids.append(str(cid))
                except Exception:
                    pass

    return ChunksManifest(
        chunks_path=str(chunks_path),
        line_count=line_count,
        sha1=file_sha1(chunks_path),
        sample_chunk_ids=sample_chunk_ids,
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"