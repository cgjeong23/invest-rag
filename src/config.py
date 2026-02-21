# src/config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBED_MODEL = "text-embedding-3-small"
RERANK_MODEL = "gpt-4.1-mini"
GEN_MODEL = "gpt-4.1-mini"
BATCH_SIZE = 64
INDEX_TYPE = "IndexFlatIP"
NORMALIZE = True

# ---- RAG context formatting ----
# Max characters to include per retrieved item (doc/chunk)
MAX_CHARS_PER_DOC = 1400

# Hard cap for total context length passed to the generator
MAX_CONTEXT_CHARS = 8000