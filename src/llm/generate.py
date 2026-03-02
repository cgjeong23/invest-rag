# src/llm/generate.py
from __future__ import annotations
import re
from openai import OpenAI
from src.config import GEN_MODEL

client = OpenAI()

def extract_cited_doc_ids(text: str) -> set[str]:
    # 너 포맷이 [doc_id] 라면 이걸로 충분
    return set(re.findall(r"\[([^\]]+)\]", text or ""))

def validate_citations(answer: str, retrieved: list[dict]) -> bool:
    valid = {r.get("doc_id") for r in retrieved if r.get("doc_id")}
    cited = extract_cited_doc_ids(answer)

    # If the model says "not enough information", allow no citations
    if "don't have enough information" in (answer or "").lower():
        return True

    # Otherwise require at least one citation, and all must be valid
    return (len(cited) > 0) and cited.issubset(valid)

def rag_generate(query: str, context: str, model: str = GEN_MODEL) -> str:
    system = (
        "You are an assistant for an investment RAG system. "
        "Answer using ONLY the provided context. "
        "Cite sources using [doc_id] for each key claim. "
        "If the context does not contain evidence, say you don't have enough information."
    )
    user = f"CONTEXT:\n{context}\n\nQUESTION:\n{query}\n\nANSWER:"

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=0
    )
    return (resp.choices[0].message.content or "").strip()

def rag_generate_with_retry(query: str, context: str, retrieved: list[dict], model: str = GEN_MODEL) -> tuple[str, bool]:
    ans1 = rag_generate(query, context, model=model)
    ok1 = validate_citations(ans1, retrieved)
    if ok1:
        return ans1, True

    # Retry: force grounding to available doc_ids
    valid_ids = [r.get("doc_id") for r in retrieved if r.get("doc_id")]
    system2 = (
        "Your previous answer used invalid or missing citations. "
        f"Retry using ONLY these doc_ids: {valid_ids}. "
        "Return an answer with correct [doc_id] citations."
    )
    user2 = f"CONTEXT:\n{context}\n\nQUESTION:\n{query}\n\nANSWER:"
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role":"system","content":system2},
                  {"role":"user","content":user2}],
        temperature=0
    )
    ans2 = (resp.choices[0].message.content or "").strip()
    ok2 = validate_citations(ans2, retrieved)
    return ans2, ok2