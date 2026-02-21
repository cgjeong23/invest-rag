from pathlib import Path

DIRS = [
    "scripts"
    "notebooks",
    "data/samples",
    "data/processed",
    "indexes/faiss",
    "eval",
    "logs",
    "docs",
    "src/data_pipeline",
    "src/retrieval",
    "src/llm",
    "src/app",
    "src/eval",
]

FILES_WITH_STARTER_CONTENT = {
    ".env.example": "OPENAI_API_KEY=\n",
    "data/README.md": "# Data\n- samples/: input sample docs (jsonl)\n- processed/: chunked outputs\n",
    "docs/data_contract.md": "# Data Contract\n",
    "docs/architecture.md": "# Architecture\n",
    "docs/evaluation.md": "# Evaluation\n",
    "README.md": "# Invest Content RAG\n",
    "src/__init__.py": "",
    "src/data_pipeline/__init__.py": "",
    "src/retrieval/__init__.py": "",
    "src/llm/__init__.py": "",
    "src/app/__init__.py": "",
    "src/eval/__init__.py": "",
}

def make_project(root: Path):
    root.mkdir(parents=True, exist_ok=True)

    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)

    for rel_path, content in FILES_WITH_STARTER_CONTENT.items():
        p = root / rel_path
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

    print("✅ Project initialized at:", root)