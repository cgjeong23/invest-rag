# src/llm/embedding.py
from __future__ import annotations

import os
import time
import random
from typing import List

import numpy as np
from tqdm import tqdm
from openai import OpenAI

from src.config import EMBED_MODEL, BATCH_SIZE


def _get_client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI()


def embed_texts(
    text_list: List[str],
    model: str = EMBED_MODEL,
    batch_size: int = BATCH_SIZE,
    max_retries: int = 5,
) -> np.ndarray:
    if not text_list:
        raise ValueError("Empty text_list passed to embed_texts.")

    client = _get_client()
    all_vecs = []

    for start in tqdm(range(0, len(text_list), batch_size), desc="Embedding"):
        batch = text_list[start:start + batch_size]

        for attempt in range(max_retries):
            try:
                resp = client.embeddings.create(model=model, input=batch)
                all_vecs.extend([d.embedding for d in resp.data])
                break
            except Exception as e:
                wait = (2 ** attempt) + random.random()
                print(f"[warn] embedding batch failed ({attempt+1}/{max_retries}): {e}")
                print(f"       sleeping {wait:.2f}s...")
                time.sleep(wait)
        else:
            raise RuntimeError("Embedding failed after max retries.")

    return np.array(all_vecs, dtype=np.float32)


def embed_query(query: str, model: str = EMBED_MODEL) -> np.ndarray:
    query = query.strip()
    if not query:
        raise ValueError("Empty query.")

    client = _get_client()
    resp = client.embeddings.create(model=model, input=[query])
    return np.array(resp.data[0].embedding, dtype=np.float32)[None, :]