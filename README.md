# invest-rag

Reproducible & Debuggable RAG Pipeline for Investment Research

FAISS (Inner Product + L2 Normalization)\
Optional LLM Rerank\
Grounded Generation with Strict Citation Validation

------------------------------------------------------------------------

## Overview

`invest-rag` is a modular Retrieval-Augmented Generation (RAG) system
designed for investment research.

It focuses on:

-   Reproducible indexing
-   Swappable retrieval strategies
-   Deterministic similarity search (Cosine via IP)
-   Strict evidence-grounded answer generation

The system separates retrieval, reranking, and generation for easier
debugging and evaluation.

------------------------------------------------------------------------

## Demo

### Query

What supports AsterFoundry's pricing premium?

### Retrieved (Top-3)

-   report_0005\
-   news_0012\
-   disclosure_0003

### Final Answer (Grounded)

AsterFoundry maintains pricing power due to process differentiation and
negotiated wafer allocation advantages.\
\[report_0005\]

------------------------------------------------------------------------

## Architecture

Documents\
→ Chunking\
→ Embedding\
→ L2 Normalization\
→ FAISS Index (Inner Product)\
→ Top-k Retrieval\
→ (Optional) LLM Rerank\
→ Grounded Generation\
→ Citation Validation

------------------------------------------------------------------------

## Key Design Decisions

### 1️⃣ Cosine Similarity via Inner Product

All vectors are L2-normalized before indexing.\
This enables cosine similarity while using FAISS Inner Product search
for efficiency.

### 2️⃣ Artifact-Driven Retrieval

Index files (`index.bin`, `meta.jsonl`) are treated as reproducible
artifacts.\
Retrieval logic is independent from generation.

### 3️⃣ Strict Citation Enforcement

The generator is forced to cite retrieved `doc_id`s only.\
A validation layer prevents hallucinated references.

------------------------------------------------------------------------

## Project Structure

invest-rag/ │ ├── data/ │ └── samples/ │ ├── indexes/ │ └── faiss/ │ ├──
scripts/ │ ├── build_chunks.py │ ├── build_index.py │ └── query.py │ ├──
src/ │ ├── retrieval/ │ ├── generation/ │ └── evaluation/ │ └──
README.md

------------------------------------------------------------------------

## Quickstart

Install dependencies:

pip install -r requirements.txt

Build index:

python scripts/build_index.py

Run query:

python scripts/query.py --query "What drives ASTF pricing?"

------------------------------------------------------------------------

## Evaluation

Supports:

-   Vector-only baseline retrieval
-   Optional LLM rerank comparison
-   Top-k overlap analysis
-   Manual answer validation

Designed to make retrieval quality measurable.

------------------------------------------------------------------------

## Roadmap

-   Add reranker scoring metrics
-   Add retrieval benchmark dataset
-   Add streaming interface
-   Add lightweight web UI

------------------------------------------------------------------------

## Why This Project

Most RAG demos blur retrieval and generation.

This project enforces:

-   Retrieval transparency
-   Reproducibility
-   Grounded generation discipline

It is designed as a minimal but production-structured RAG system.

## Documentation

For detailed technical documentation:

- Architecture design → docs/architecture.md
- Data contract specification → docs/data_contract.md
- Evaluation methodology → docs/evaluation.md