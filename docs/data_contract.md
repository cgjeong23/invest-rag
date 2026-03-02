# Data Contract

This project operates on SEC 10-K filings (2024) and enforces a strict schema to ensure:

- Reproducible indexing
- Stable evaluation
- Deterministic retrieval behavior
- Doc-level and chunk-level benchmarking

All datasets are stored in JSONL format (one JSON object per line).

---

# 1. Raw Section-Level Documents

File:
data/samples/sec_docs.jsonl

Granularity:
One SEC section per document (e.g., Item 1 - Business)

Required Fields:

- doc_id: string  
  Example: nvidia_2024_item_1_business  
  Format: {company}_{year}_{section_slug}

- company: string  
  Example: NVIDIA

- year: integer  
  Example: 2024

- section: string  
  Example: Item 1 - Business

- source: string  
  Example: sec_10k_html

- content: string  
  Full section text used as input to chunking.

Invariants:

- doc_id must uniquely identify a single SEC section.
- year must be consistent across corpus (currently 2024).
- content must be raw section text prior to chunking.

---

# 2. Processed Chunk-Level Data

File:
data/processed/chunks.jsonl

Granularity:
Deterministic semantic chunks derived from section-level documents.

Required Fields:

- chunk_id: string  
  Example: nvidia_2024_item_1_business_c105_8c50e4f37be5  
  Format: {doc_id}_c{chunk_index}_{hash}

- chunk_index: integer  
  Position within section.

- text: string  
  Chunk text used for embedding.

Notes:

- chunk_id must be deterministic (same input produces same ID).
- chunk_index preserves ordering within section.
- text is the embedding input field.

---

# 3. FAISS Metadata

File:
indexes/faiss/meta.jsonl

Granularity:
One row per embedded chunk.

Required Fields:

- chunk_id: string
- doc_id: string
- company: string
- year: integer
- section: string
- source: string
- content: string (same semantic text as chunk input)

Invariants:

- meta.jsonl ordering must align exactly with index.bin vector ordering.
- Each vector corresponds to one chunk_id.
- doc_id enables doc-level evaluation.
- chunk_id enables evidence-level evaluation.

---

# 4. Evaluation Questions

File:
eval/questions.jsonl

Granularity:
One evaluation query per line.

Required Fields:

- qid: string  
  Example: A_001

- query: string  
  Natural language question.

- gold_doc_ids: list[string]  
  Section-level ground truth.

- gold_chunk_ids: list[string]  
  Evidence-level ground truth.

Optional Fields:

- tier: string (A / B / C)
- type: string (cross_company_implicit, etc.)
- notes: string (annotation metadata)

Evaluation Compatibility:

- Doc-level evaluation uses id_key="doc_id" and dedupe=True.
- Chunk-level evaluation uses id_key="chunk_id" and dedupe=False.

---

# Identifier Hierarchy

doc_id → Section-level structural retrieval  
chunk_id → Evidence-level precision retrieval  

This separation enables:

- Recall benchmarking at section level
- Precision benchmarking at evidence level
- Clear attribution of rerank improvements

---

# Reproducibility Guarantees

The following artifacts guarantee deterministic rebuild:

- build_config.json
- chunks_manifest.json
- index.bin
- meta.jsonl

Rebuilding with identical inputs must produce:

- Identical chunk_ids
- Identical vector ordering
- Identical evaluation results (given same model)

---

# Design Intent

The data contract is structured to:

- Support multi-granularity evaluation
- Enable measurable retrieval improvements
- Avoid hidden schema coupling
- Preserve citation grounding integrity

This contract prioritizes reproducibility, measurement clarity, and engineering transparency over minimal schema complexity.
