# src/retrieval/build_vector_index.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import faiss

from src.config import EMBED_MODEL, BATCH_SIZE, INDEX_TYPE, NORMALIZE
from src.llm.embedding import embed_texts
from src.retrieval.chunk_loader import load_chunks_for_index
from src.retrieval.vector_store import l2_normalize

from src.retrieval.artifacts import build_chunks_manifest, write_json, utc_now_iso  


@dataclass(frozen=True)
class BuildIndexResult:
    index_path: str
    meta_path: str
    n_vectors: int
    dim: int


def build_vector_index(
    *,
    chunks_path: Path,
    index_path: Path,
    meta_path: Path,
    embed_model: str = EMBED_MODEL,
    batch_size: int = BATCH_SIZE,
    index_type: str = INDEX_TYPE,
    normalize: bool = NORMALIZE,
    save_text_in_meta: bool = True,
) -> BuildIndexResult:
    # 1) load texts (deterministic) + filter empty
    res = load_chunks_for_index(chunks_path, sort_by_chunk_id=True, drop_empty_texts=True)

    # 2) embed
    vecs = embed_texts(res.texts, model=embed_model, batch_size=batch_size)
    vecs = np.asarray(vecs, dtype=np.float32)

    # 3) normalize for cosine
    if normalize:
        vecs = l2_normalize(vecs)

    # 4) build FAISS
    dim = int(vecs.shape[1])
    if index_type != "IndexFlatIP":
        raise ValueError(f"Unsupported index_type for now: {index_type} (use IndexFlatIP)")

    index = faiss.IndexFlatIP(dim)
    assert vecs.shape[1] == index.d, "Embedding dimension mismatch with FAISS index."
    index.add(vecs)

    # 5) save index + meta
    index_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_path))

    with meta_path.open("w", encoding="utf-8") as f:
        for cid, t, m in zip(res.chunk_ids, res.texts, res.metas):
            row = {"chunk_id": cid, **m}
            if save_text_in_meta:
                row["text"] = t
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # 6) save reproducibility artifacts next to the index
    out_dir = index_path.parent

    # a) build_config.json
    build_config = {
        "created_at": utc_now_iso(),
        "embed_model": embed_model,
        "batch_size": batch_size,
        "normalize": normalize,
        "faiss_index": index_type,
        "save_text_in_meta": save_text_in_meta,
        "n_vectors": int(index.ntotal),
        "embedding_dim": int(index.d),
        "chunks_path": str(chunks_path),
        "index_path": str(index_path),
        "meta_path": str(meta_path),
    }
    write_json(out_dir / "build_config.json", build_config)

    # b) chunks_manifest.json (sha1 + line_count + sample ids)
    manifest = build_chunks_manifest(chunks_path, sample_n=5)
    write_json(out_dir / "chunks_manifest.json", {
        "chunks_path": manifest.chunks_path,
        "line_count": manifest.line_count,
        "sha1": manifest.sha1,
        "sample_chunk_ids": manifest.sample_chunk_ids,
    })

    return BuildIndexResult(
        index_path=str(index_path),
        meta_path=str(meta_path),
        n_vectors=index.ntotal,
        dim=index.d,
    )