# Designing a Measurable Retrieval System

## 🔬 Full Reproducibility & Technical Details

For:
- exact setup instructions
- evaluation reproduction
- FAISS index artifacts
- directory structure
- detailed implementation notes

See: [README_TECHNICAL.md](README_TECHNICAL.md)

## From Deterministic Vector Search to LLM Reranking

This project is not a notebook demo of RAG.

It is a structured retrieval system built to answer one core question:

**How do we measure and systematically improve retrieval quality in
production-like settings?**

Instead of focusing only on generation, this project isolates and
evaluates:

-   Vector retrieval behavior
-   Ranking quality vs recall expansion
-   Document-level vs chunk-level difficulty
-   LLM reranking as ranking correction
-   Citation-grounded generation
-   Out-of-distribution safety behavior

------------------------------------------------------------------------

# Problem Framing

Most RAG demos: - Retrieve top-k - Pass to LLM - Hope for better answers

This system separates concerns:

1.  Retrieval quality must be measurable.
2.  Ranking quality matters more than increasing k.
3.  Chunk-level retrieval is fundamentally harder than document-level
    retrieval.
4.  Hallucination must be structurally prevented, not prompt-controlled.

------------------------------------------------------------------------

# System Overview

Pipeline:

SEC 10-K → Chunking → Embedding (L2 normalized) → FAISS (Inner Product)
→ Vector Retrieval → Optional LLM Rerank → Grounded Generation

All components are modular and independently testable.

------------------------------------------------------------------------

# Core Design Decisions

### 1. L2 Normalization + Inner Product (FAISS)

-   Converts cosine similarity into efficient inner product search.
-   Enables deterministic similarity computation.

Trade-off: - Requires strict normalization discipline.

------------------------------------------------------------------------

### 2. Deterministic Chunk IDs

-   Ensures reproducibility across rebuilds.
-   Enables evaluation stability.

------------------------------------------------------------------------

### 3. Retrieval / Rerank / Generation Separation

-   Retrieval is evaluated independently from generation.
-   Allows benchmarking of ranking behavior without LLM noise.

------------------------------------------------------------------------

### 4. Ranking Correction, Not Recall Expansion

Evaluation results show:

-   Vector retriever already achieves high recall at k=10.
-   Reranking improves MRR significantly without increasing recall.
-   Improvement comes from correcting ordering, not widening search.

This reflects real-world systems where latency constraints limit k.

------------------------------------------------------------------------

# Evaluation Strategy

Benchmark: 40 curated cross-company questions.

Metrics: - Recall@k - Mean Reciprocal Rank (MRR)

Two evaluation levels: - Document-level (section retrieval) -
Chunk-level (evidence retrieval)

Findings:

-   Document retrieval is relatively easy.
-   Chunk retrieval is significantly harder.
-   Reranking meaningfully improves ranking quality at low k.
-   Most gains appear in top-1 correction.

This validates that ranking quality dominates depth expansion.

------------------------------------------------------------------------

# Safety: Out-of-Distribution Handling

When queried about a non-indexed entity:

-   No hallucinated answer
-   Explicit insufficient-evidence response
-   Citation validation enforced

Grounded refusal is structural, not prompt-based.

------------------------------------------------------------------------

# Engineering Considerations

-   Reproducible chunk manifests
-   Logged retrieval debugging
-   Modular directory structure
-   CLI-based full pipeline execution
-   Evaluation artifacts saved separately

The system is structured like a small production service, not a research
notebook.

------------------------------------------------------------------------

# What This Demonstrates

This project reflects how I approach retrieval systems:

-   Separate concerns before optimizing
-   Measure before improving
-   Improve ranking before expanding search depth
-   Prefer structural safety over prompt tricks
-   Build modular systems that scale beyond a single dataset

------------------------------------------------------------------------

# Target Role Alignment

This repository is designed to demonstrate readiness for:

-   ML Engineer (Retrieval / Search)
-   LLM Infrastructure Intern
-   Applied AI Engineer
-   Agent System Engineer

The focus is not on prompt engineering, but on measurable system
behavior.
