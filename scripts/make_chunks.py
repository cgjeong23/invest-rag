import argparse
import hashlib
import json
import re
from pathlib import Path


HEADER_PATTERNS = [
    r"^\s*요약\s*[:：]\s*",
    r"^\s*Summary\s*[:：]\s*",
    r"^\s*핵심\s*[:：]\s*",
]


def clean_text(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    t = t.replace("\u00a0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    for pat in HEADER_PATTERNS:
        t = re.sub(pat, "", t)
    return t.strip()


def split_sentences(text: str):
    """
    Simple regex sentence splitter for mixed Korean/English text.
    """
    t = re.sub(r"\s*\n\s*", " ", text.strip())
    if not t:
        return []
    parts = re.split(r"(?<=[\.\!\?])\s+|(?<=다\.)\s+", t)
    return [p.strip() for p in parts if p.strip()]


def chunk_sentences(sents, max_chars=450, overlap_sents=1):
    chunks = []
    cur = []
    cur_len = 0

    def flush():
        nonlocal cur, cur_len
        if cur:
            chunks.append(" ".join(cur).strip())
        cur = []
        cur_len = 0

    for s in sents:
        if not cur:
            cur = [s]
            cur_len = len(s)
            continue

        if cur_len + 1 + len(s) <= max_chars:
            cur.append(s)
            cur_len += 1 + len(s)
        else:
            flush()
            if overlap_sents > 0 and chunks:
                prev_sents = split_sentences(chunks[-1])
                prefix = prev_sents[-overlap_sents:] if len(prev_sents) >= overlap_sents else prev_sents
                cur = prefix + [s]
                cur_len = sum(len(x) for x in cur) + (len(cur) - 1)
            else:
                cur = [s]
                cur_len = len(s)

    flush()
    return chunks


def make_chunk_id(doc_id: str, chunk_index: int, chunk_text: str) -> str:
    h = hashlib.sha1(f"{doc_id}|{chunk_index}|{chunk_text}".encode("utf-8")).hexdigest()[:12]
    return f"{doc_id}_c{chunk_index:02d}_{h}"


def doc_to_chunks(doc, max_chars=450, overlap_sents=1):
    content = clean_text(doc.get("content", ""))
    sents = split_sentences(content)

    if len(content) <= max_chars:
        chunk_texts = [content] if content else []
    else:
        chunk_texts = chunk_sentences(sents, max_chars=max_chars, overlap_sents=overlap_sents)

    out = []
    meta = {k: doc.get(k) for k in ["doc_id", "company", "year", "section", "source", "content"]}
    for i, ct in enumerate(chunk_texts):
        out.append(
            {
                "chunk_id": make_chunk_id(doc["doc_id"], i, ct),
                "chunk_index": i,
                "text": ct,
                "metadata": meta,
            }
        )
    return out


def load_jsonl(path: Path):
    docs = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_path", type=str, default="data/samples/sec_docs.jsonl")
    parser.add_argument("--out_path", type=str, default="data/processed/chunks.jsonl")
    parser.add_argument("--max_chars", type=int, default=450)
    parser.add_argument("--overlap_sents", type=int, default=1)
    args = parser.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)

    docs = load_jsonl(in_path)
    all_chunks = []
    for d in docs:
        all_chunks.extend(doc_to_chunks(d, max_chars=args.max_chars, overlap_sents=args.overlap_sents))

    write_jsonl(out_path, all_chunks)

    print(f"[OK] docs={len(docs)} chunks={len(all_chunks)}")
    print(f"[OK] wrote: {out_path}")


if __name__ == "__main__":
    main()