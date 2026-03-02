# Architecture

## System Overview

This project implements a modular Retrieval-Augmented Generation (RAG) system over SEC 10-K filings.

The system is intentionally decomposed into:

1. Data ingestion and chunking  
2. Embedding and indexing  
3. Vector retrieval  
4. Optional LLM reranking  
5. Grounded generation  
6. Citation validation  
7. Independent evaluation  

Each layer is independently testable and replaceable.

---

## High-Level Pipeline

SEC 10-K (Section-Level Documents)
        ↓
Deterministic Chunking (~4000 chunks)
        ↓
Embedding + L2 Normalization
        ↓
FAISS Index (Inner Product)
        ↓
Top-k Vector Retrieval
        ↓
Optional LLM Reranking
        ↓
Grounded Answer Generation
        ↓
Citation Validation

---

## Design Philosophy

### Retrieval vs Reranking Separation

Retrieval and reranking are intentionally separated because they optimize different objectives.

Retrieval is optimized for recall:

- Fast similarity search  
- Maximize probability that the correct document appears in top-k  
- Deterministic and reproducible  

Reranking is optimized for ranking quality:

- Operates on a small candidate set  
- Performs deeper semantic reasoning  
- Promotes the most relevant evidence to top-1  

This separation allows:

- Independent benchmarking  
- Swappable rerank models  
- Clear attribution of performance gains  

In practice, high recall at k=10 ensures that reranking operates on a sufficiently strong candidate pool.

---

## Similarity Design: Cosine via Inner Product

All embeddings are L2-normalized before indexing.

Cosine similarity between two vectors is equivalent to their inner product after normalization.

Because of this property, FAISS IndexFlatIP can be used to perform cosine similarity search efficiently and deterministically.

This design provides:

- Computational efficiency  
- Stable ranking behavior  
- Clear similarity interpretation  
- Fully reproducible search  

---

## Identifier Granularity

Two identifier levels are intentionally separated.

### doc_id (Section-Level)

Represents a single SEC section.

Example:

apple_2024_item_1_business

Used for:

- Document-level evaluation  
- Structural retrieval analysis  
- Citation references  

---

### chunk_id (Evidence-Level)

Represents a deterministic semantic chunk.

Example:

nvidia_2024_item_1_business_c02_085ed035dcb2

Used for:

- Evidence-level evaluation  
- Fine-grained ranking analysis  
- Citation grounding precision  

This dual-granularity design enables:

- Structural retrieval measurement at the section level  
- Evidence precision measurement at the chunk level  

---

## Why Chunk-Level Evaluation Matters

Document-level retrieval measures:

“Did we retrieve the correct section?”

Chunk-level retrieval measures:

“Did we retrieve the correct evidence?”

Chunk-level performance is significantly harder and exposes ranking weaknesses that document-level metrics may hide.

This mirrors real-world RAG behavior where evidence precision matters more than section-level correctness.

---

## Deterministic Artifacts

The system treats index artifacts as reproducible components:

- chunks_manifest.json  
- build_config.json  
- index.bin  
- meta.jsonl  

This ensures:

- Identical index rebuilding  
- Stable evaluation results  
- Debuggable retrieval behavior  

---

## Grounded Generation and Citation Validation

Generation is strictly constrained to retrieved context.

Validation enforces:

- All cited doc_ids must appear in retrieved results  
- No hallucinated references  
- Citation formatting integrity  

This enforces grounded generation discipline rather than free-form completion.

---

## Failure Modes and Tradeoffs

### Ambiguous Cross-Company Queries

Vector retrieval may confuse similar structural language across companies.

Mitigation:

- LLM reranking  
- Larger candidate pools  

---

### Multi-Part Questions

Questions spanning multiple facts may require:

- Broader retrieval  
- Query decomposition (future improvement)

---

### Out-of-Distribution Entities

If an entity is not indexed:

- The system abstains  
- No unsupported claims are generated  

Safety is prioritized over speculative completion.

---

## Engineering Tradeoffs

| Component | Design Choice | Tradeoff |
|-----------|--------------|----------|
| Index | FAISS IndexFlatIP | Exact search, not approximate |
| Similarity | L2-normalized inner product | Requires strict normalization |
| Chunking | Deterministic | May split semantic units |
| Rerank | LLM-based | Higher latency |
| Evaluation | Offline benchmark | Not latency-optimized |

The architecture prioritizes:

- Reproducibility  
- Measurable performance  
- Debuggability  
- Transparency  

over:

- Minimal latency  
- Black-box heuristics  

---

## Summary

This architecture demonstrates:

- Clear separation of recall and ranking quality  
- Deterministic similarity design  
- Multi-granularity evaluation  
- Evidence-grounded generation  
- Safe failure handling  

The goal is not simply to use RAG, but to build a system whose behavior can be measured, reasoned about, and systematically improved.