# Evaluation

This document describes how retrieval quality is measured in this project and how to interpret the results.

The goal is to evaluate a production-structured RAG pipeline with measurable retrieval behavior, not just to produce good-looking answers.

---

## Evaluation Levels

This project supports two granularities:

### 1 Document-level (Section-level)

Question is counted correct if any retrieved item matches one of the `gold_doc_ids`.

- id_key: doc_id
- dedupe: True (avoid counting multiple chunks from the same section as extra hits)

Interpretation:
- Measures whether the system finds the correct SEC section.
- Useful for structural recall and cross-company document routing.

### 2 Chunk-level (Evidence-level)

Question is counted correct if any retrieved item matches one of the `gold_chunk_ids`.

- id_key: chunk_id
- dedupe: False

Interpretation:
- Measures whether the system retrieves the exact evidence chunk.
- Much harder than doc-level and more representative of grounding precision.

---

## Metrics

### Recall@k

Recall@k is the fraction of queries where at least one gold id appears in the top-k retrieved results.

- High Recall@10 indicates strong candidate coverage.
- Recall@1 is effectively top-1 accuracy for retrieval.

### MRR@k (Mean Reciprocal Rank)

MRR@k rewards earlier placement of the first correct item.

- MRR increases when the correct document/chunk moves closer to rank 1.
- Especially informative for reranking, where recall may not change but ranking quality improves.

---

## Benchmark Dataset

File:
eval/questions.jsonl

- Size: 40 questions
- Labels: gold_doc_ids and gold_chunk_ids
- Annotated fields (optional): tier, type, notes

Typical question types include:

- cross-company implicit queries (company not explicitly mentioned)
- list/definition questions (high precision anchors)
- numeric or table-backed questions
- hard ranking cases (vector retrieval top-10 contains gold, but top-1 is wrong)

---

## Retrieval Variants Compared

### Vector Baseline

- Vector retrieval from FAISS index using L2-normalized embeddings
- Returns top-k candidates by similarity score

### LLM Rerank (Top-1 Promotion)

- Retrieves k_vec candidates from vector baseline
- Uses an LLM to choose the best candidate
- Promotes the chosen candidate to rank #1
- Returns final top-k

Important:
- Reranking does not increase recall by searching more; it mainly improves ranking quality within the same candidate pool.

---

## Results Summary

### Document-level Results

| k  | Vector R@k | Vector MRR | Rerank R@k | Rerank MRR | ΔRecall | ΔMRR |
|----|------------|------------|------------|------------|---------|------|
| 1  | 0.750 | 0.7500 | 0.875 | 0.8750 | +0.125 | +0.1250 |
| 3  | 0.850 | 0.8000 | 0.925 | 0.9000 | +0.075 | +0.1000 |
| 5  | 0.900 | 0.8188 | 0.950 | 0.9125 | +0.050 | +0.0938 |
| 10 | 0.975 | 0.8375 | 0.975 | 0.9208 | +0.000 | +0.0833 |

Interpretation:
- Vector retrieval already achieves high candidate recall (R@10 = 0.975).
- Reranking provides meaningful gains at k=1 and strong MRR improvements at all k.
- This indicates the main bottleneck is ranking quality, not candidate recall.

---

### Chunk-level Results

| k  | Vector R@k | Vector MRR | Rerank R@k | Rerank MRR | ΔRecall | ΔMRR |
|----|------------|------------|------------|------------|---------|------|
| 1  | 0.150 | 0.1500 | 0.350 | 0.3500 | +0.200 | +0.2000 |
| 3  | 0.425 | 0.2792 | 0.525 | 0.4375 | +0.100 | +0.1583 |
| 5  | 0.525 | 0.3017 | 0.575 | 0.4488 | +0.050 | +0.1471 |
| 10 | 0.625 | 0.3135 | 0.625 | 0.4544 | +0.000 | +0.1408 |

Interpretation:
- Chunk-level retrieval is substantially harder than doc-level retrieval.
- Recall@10 is capped by the difficulty of retrieving the exact evidence chunk.
- Reranking yields large MRR gains, showing it consistently promotes the correct evidence closer to rank 1.

---

## Qualitative Example: Reranking Fixes Cross-Company Ambiguity

Query:
Which product is described as the company’s first spatial computer, and what operating system is it based on?

Observed behavior:
- Vector top-1 ranked Microsoft/AMD business sections higher due to generic phrasing.
- Reranking promoted apple_2024_item_1_business to rank 1.
- Generation succeeded only after the correct section was ranked first.

Takeaway:
- Reranking improves top-1 routing for ambiguous queries even when recall@10 is unchanged.

---

## Failure Analysis Artifacts

The evaluation pipeline writes failure logs for inspection:

- fails_vector_doc_k1.jsonl
- fails_vector_doc_k10.jsonl
- fails_vector_chunk_k1.jsonl
- fails_vector_chunk_k10.jsonl

These logs are used to:
- identify systematic confusion patterns
- generate hard subsets for targeted benchmarking
- validate whether failures are retrieval vs ranking vs labeling issues

---

## Out-of-Distribution (OOD) Safety Check

When asked about an entity not in the indexed corpus (e.g., Tesla):

- the system abstains rather than hallucinating
- returns an insufficient-evidence answer
- maintains citation validity

This demonstrates grounded refusal and citation integrity.

---

## Limitations and Next Improvements

Likely improvements that could increase chunk-level recall:

- Query decomposition for multi-part questions
- Better chunking around list/table boundaries
- Dedicated rerank models (cross-encoder or hybrid rerank)
- Adding lightweight metadata filtering before retrieval (company/year/section priors)

The current focus is on measurable and reproducible retrieval behavior rather than maximizing raw accuracy via ad-hoc prompting.
