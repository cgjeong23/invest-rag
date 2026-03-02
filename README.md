# invest-rag

**Production-Structured RAG System with Measurable Retrieval Performance**

Vector Retrieval + LLM Reranking  
Document-Level & Chunk-Level Benchmarking  
Strict Citation-Grounded Generation  

---
## 🚀 Run the Full Pipeline (CLI)

You can run the full retrieval + rerank pipeline from the command line:

```bash
python src/app/cli.py \
    --query "Which company discusses ecosystem lock-in as a competitive moat?" \
    --top_k 5 \
    --rerank
```
---

## Overview

`invest-rag` is a reproducible Retrieval-Augmented Generation (RAG) system built over multiple SEC 10-K filings (2024).

The goal of this project is not just to implement RAG, but to:

- Quantitatively measure retrieval quality (Recall@k, MRR)
- Compare vector-only retrieval vs LLM-based reranking
- Evaluate document-level vs chunk-level behavior
- Enforce strict citation grounding
- Demonstrate safe out-of-distribution handling

All components (retrieval, rerank, generation, evaluation) are modular and independently testable.

---

## Dataset

Indexed SEC 10-K filings (2024):

- Apple
- NVIDIA
- Microsoft
- Meta
- AMD

Granularity:

- **Document-level:** SEC section (e.g., `apple_2024_item_1_business`)
- **Chunk-level:** ~4000 deterministic semantic chunks

Each chunk contains:

- chunk_id
- doc_id
- company
- year
- section
- content

---

## System Architecture

                ┌────────────────────┐
                │   SEC 10-K Files   │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │   Chunking Layer   │
                │  (~4000 chunks)    │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │   Embedding Model  │
                │ (L2 Normalization) │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │     FAISS Index    │
                │   (Inner Product)  │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │   Vector Retrieval │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │   LLM Reranker     │ (optional)
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │  Grounded Generate │
                │ + Citation Check   │
                └────────────────────┘

---

## Evaluation Results

Evaluation benchmark: 40 curated cross-company questions.

### Document-Level Performance

| k  | Vector R@k | Vector MRR | Rerank R@k | Rerank MRR | ΔRecall | ΔMRR |
|----|------------|------------|------------|------------|---------|------|
| 1  | 0.750 | 0.7500 | 0.875 | 0.8750 | +0.125 | +0.1250 |
| 3  | 0.850 | 0.8000 | 0.925 | 0.9000 | +0.075 | +0.1000 |
| 5  | 0.900 | 0.8188 | 0.950 | 0.9125 | +0.050 | +0.0938 |
| 10 | 0.975 | 0.8375 | 0.975 | 0.9208 | +0.000 | +0.0833 |

Key insight:
- High recall from vector retriever (R@10 = 0.975)
- Significant top-1 improvement from LLM reranking
- Rerank improves ranking quality without increasing candidate depth

---

### Chunk-Level Performance

| k  | Vector R@k | Vector MRR | Rerank R@k | Rerank MRR | ΔRecall | ΔMRR |
|----|------------|------------|------------|------------|---------|------|
| 1  | 0.150 | 0.1500 | 0.350 | 0.3500 | +0.20 | +0.2000 |
| 3  | 0.425 | 0.2792 | 0.525 | 0.4375 | +0.10 | +0.1583 |
| 5  | 0.525 | 0.3017 | 0.575 | 0.4488 | +0.05 | +0.1471 |
| 10 | 0.625 | 0.3135 | 0.625 | 0.4544 | +0.00 | +0.1408 |

Key insight:
- Chunk-level retrieval is substantially harder.
- Reranking provides large MRR gains, meaning it promotes the correct evidence chunk toward the top.
- Improvement is primarily ranking correction, not recall expansion.

---

## Safety: Out-of-Distribution Handling

Query example:
"Explain Risk Factors of the company Tesla."

Tesla is not indexed.

System behavior:

- No hallucinated Tesla information
- Explicit insufficient-evidence response
- Citation validation remains true

This demonstrates grounded refusal rather than hallucinated generation.

---

## Project Structure

---
invest-rag/
├── data/
│   ├── README.md
│   ├── processed/
│   │   ├── build_config.json
│   │   ├── chunks.jsonl
│   │   └── chunks_manifest.json
│   └── samples/
│       └── sec_docs.jsonl
│
├── docs/
│   ├── architecture.md
│   ├── data_contract.md
│   └── evaluation.md
│
├── eval/
│   ├── questions.jsonl
│   ├── results_vector_doc.json
│   ├── results_vector_chunk.json
│   ├── results_rerank_llm_doc.json
│   ├── results_rerank_llm_chunk.json
│   ├── fails_vector_doc_k1.jsonl
│   ├── fails_vector_doc_k10.jsonl
│   ├── fails_vector_chunk_k1.jsonl
│   └── fails_vector_chunk_k10.jsonl
│
├── indexes/
│   └── faiss/
│       ├── index.bin
│       ├── meta.jsonl
│       ├── build_config.json
│       └── chunks_manifest.json
│
├── logs/
│   ├── retrieval_debug.jsonl
│   └── run_logs.jsonl
│
├── notebooks/
│   ├── 00_setup_and_ingest.ipynb
│   ├── 01_build_vector_index.ipynb
│   ├── 02_evaluate_retrieval.ipynb
│   └── 03_rag_generate.ipynb
│
├── scripts/
│   └── init_project.py
│
└── src/
    ├── config.py
    ├── __init__.py
    │
    ├── app/
    │   ├── cli.py
    │   ├── rag_runtime.py
    │   └── __init__.py
    │
    ├── data_pipeline/
    │   ├── io_utils.py
    │   └── __init__.py
    │
    ├── retrieval/
    │   ├── artifacts.py
    │   ├── build_vector_index.py
    │   ├── chunk_loader.py
    │   ├── vector_store.py
    │   └── __init__.py
    │
    ├── llm/
    │   ├── embedding.py
    │   ├── rerank.py
    │   ├── generate.py
    │   ├── context.py
    │   └── __init__.py
    │
    └── eval/
        ├── retrieval_eval.py
        ├── retrieval_logging.py
        ├── search_wrappers.py
        └── __init__.py
---

## What This Demonstrates

- Deterministic FAISS-based similarity search
- Measurable retrieval benchmarking
- Semantic reranking improvements
- Document vs chunk-level evaluation
- Strict citation-grounded generation
- Safe handling of unsupported entities

This project is structured to resemble a production-ready RAG system rather than a notebook prototype.
