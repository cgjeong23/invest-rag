# src/app/cli.py
from __future__ import annotations

from pathlib import Path

from src.retrieval.build_vector_index import build_vector_index
from src.eval.retrieval_eval import read_questions, run_eval_suite
from src.llm.embedding import embed_query
from src.retrieval.vector_store import VectorStore
from src.eval.search_wrappers import make_vectorstore_search_fn, make_llm_rerank_search_fn

# (optional) runtime helper: context+generate
from src.llm.context import build_context
from src.llm.generate import rag_generate_with_retry


def main():
    root = Path.cwd().resolve()
    assert (root / "src").exists(), f"Run from project root (invest-rag/). cwd={root}"

    # paths
    chunks_path = root / "data" / "processed" / "chunks.jsonl"
    index_dir   = root / "indexes" / "faiss"
    index_path  = index_dir / "index.bin"
    meta_path   = index_dir / "meta.jsonl"
    q_path      = root / "eval" / "questions.jsonl"
    eval_dir    = root / "eval"

    # 1) build index (only if missing)
    if not index_path.exists() or not meta_path.exists():
        print("[1/3] Building index...")
        build_vector_index(
            chunks_path=chunks_path,
            index_path=index_path,
            meta_path=meta_path,
            save_text_in_meta=True,
        )
    else:
        print("[1/3] Index exists. Skip build.")

    # 2) eval (vector vs rerank)
    print("[2/3] Running eval...")
    questions = read_questions(q_path)

    vs = VectorStore.load(index_path=index_path, meta_path=meta_path)
    vector_search_fn = make_vectorstore_search_fn(vs, embed_query=embed_query, normalize=True)
    rerank_search_fn = make_llm_rerank_search_fn(vector_search_fn, k_vec=10)

    vec_out = eval_dir / "results_vector_doc.json"
    rr_out  = eval_dir / "results_rerank_llm_doc.json"

    vec_suite = run_eval_suite(questions, ks=(1, 3, 5, 10), search_fn=vector_search_fn, out_path=vec_out, id_key="doc_id", dedupe=True)
    rr_suite  = run_eval_suite(questions, ks=(1, 3, 5, 10), search_fn=rerank_search_fn, out_path=rr_out,  id_key="doc_id", dedupe=True)

    v_mrr1 = vec_suite["results"]["1"]["mrr_at_k"]
    r_mrr1 = rr_suite["results"]["1"]["mrr_at_k"]
    print(f"[eval] Vector MRR@1={v_mrr1:.4f} | Rerank MRR@1={r_mrr1:.4f} | Δ={r_mrr1 - v_mrr1:+.4f}")
    print(f"[eval] wrote: {vec_out}")
    print(f"[eval] wrote: {rr_out}")

    # 3) demo answers (few queries)
    print("[3/3] Demo queries (vector vs rerank)...")
    demo_queries = [
        "Which product is described as the company’s first spatial computer, and what operating system is it based on?",
        "In Apple’s Home product description, which device is a media streaming and gaming device, and which operating system is it based on?",
    ]

    def run_once(q: str, search_fn, label: str):
        retrieved = search_fn(q, 5)

        top = retrieved[0] if retrieved else {}
        top_doc = top.get("doc_id")
        top_section = top.get("section")
        top_snippet = (top.get("text") or top.get("content") or "")[:220].replace("\n", " ")

        ctx = build_context(retrieved)
        ans, citations_valid = rag_generate_with_retry(q, ctx, retrieved)

        print("\n" + "-" * 90)
        print(f"[{label}] Q: {q}")
        print(f"[{label}] top1_doc: {top_doc}")
        if top_section:
            print(f"[{label}] top1_section: {top_section}")
        print(f"[{label}] citations_valid: {citations_valid}")
        print(f"[{label}] top1_snippet: {top_snippet}")
        print(f"[{label}] answer:\n{ans}")

    for q in demo_queries:
        run_once(q, vector_search_fn, "VECTOR")
        run_once(q, rerank_search_fn, "RERANK")


if __name__ == "__main__":
    main()