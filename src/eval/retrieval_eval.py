# src/eval/retrieval_eval.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable
import numpy as np


SearchFn = Callable[[str, int], list[dict]]  # query, k -> ranked results (dicts)


def read_questions(path: Path) -> list[dict]:
    # (중복 싫으면 src.data_pipeline.io_utils.read_jsonl로 대체 가능)
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _dedupe_keep_order(items: Iterable[str], k: int) -> list[str]:
    seen = set()
    out = []
    for x in items:
        if x is None:
            continue
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
        if len(out) >= k:
            break
    return out


def evaluate_retrieval(
    questions: list[dict],
    *,
    k: int,
    search_fn: SearchFn,
    id_key: str = "doc_id",           # "doc_id" (doc-level) or "chunk_id" (chunk-level)
    dedupe: bool = True,              # doc-level 평가면 True 추천
    save_fail_path: Path | None = None,
):
    recalls: list[float] = []
    mrrs: list[float] = []
    fails: list[dict] = []
    skipped_no_gold = 0

    for q in questions:
        qid = q["qid"]
        query = q["query"]
        gold = set(q.get("gold_doc_ids", []))  # 현재 질문 포맷 기준

        if not gold:
            skipped_no_gold += 1
            continue

        res = search_fn(query, k)  # ✅ evaluator가 컷오프 k 통제
        pred_ids = [r.get(id_key) for r in res if r.get(id_key)]

        topk = _dedupe_keep_order(pred_ids, k) if dedupe else pred_ids[:k]

        # ✅ Recall@k (진짜 recall)
        hit_count = len(set(topk) & gold)
        recall = hit_count / len(gold)
        recalls.append(recall)

        # ✅ MRR@k
        rr = 0.0
        for i, pid in enumerate(topk, start=1):
            if pid in gold:
                rr = 1.0 / i
                break
        mrrs.append(rr)

        if hit_count == 0:
            fails.append({
                "qid": qid,
                "query": query,
                "gold_ids": list(gold),
                "top5": res[:5],
            })

    metrics = {
        "k": k,
        "n": len(questions),
        "n_scored": len(recalls),
        "skipped_no_gold": skipped_no_gold,
        "recall_at_k": float(np.mean(recalls)) if recalls else 0.0,
        "mrr_at_k": float(np.mean(mrrs)) if mrrs else 0.0,
        "n_fail": len(fails),
    }

    if save_fail_path:
        save_fail_path.parent.mkdir(parents=True, exist_ok=True)
        with save_fail_path.open("w", encoding="utf-8") as f:
            for row in fails:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return metrics, fails


def run_eval_suite(
    questions: list[dict],
    *,
    ks=(1, 3, 5, 10),
    search_fn: SearchFn,
    out_path: Path | None = None,
    id_key: str = "doc_id",
    dedupe: bool = True,
):
    suite = {"ks": list(ks), "results": {}}

    for k in ks:
        m, _ = evaluate_retrieval(
            questions,
            k=k,
            search_fn=search_fn,
            id_key=id_key,
            dedupe=dedupe,
            save_fail_path=None,
        )
        suite["results"][str(k)] = m

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(suite, ensure_ascii=False, indent=2), encoding="utf-8")

    return suite