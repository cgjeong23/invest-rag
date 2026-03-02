# Data Directory

This directory contains processed artifacts used by the RAG pipeline.

## Structure

- processed/
  - chunks.jsonl: deterministic text chunks used to build the FAISS index
  - chunks_manifest.json: SHA-1 + line count for reproducibility
  - build_config.json: chunking configuration

- samples/
  - sec_docs.jsonl: sample SEC documents (cleaned JSON format)

## Notes

- The FAISS index is built from `processed/chunks.jsonl`.
- Index reproducibility is tracked via `chunks_manifest.json`.
- Raw HTML parsing is not included in this repository.