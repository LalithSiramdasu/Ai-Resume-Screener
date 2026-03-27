import os
from dotenv import load_dotenv

load_dotenv()

# API keys & provider configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").strip().lower() or "groq"

# Server
PORT = int(os.getenv("PORT", "8000"))

# Directories
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db")

# Model Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# Chunking Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)


def can_use_groq() -> bool:
    return LLM_PROVIDER == "groq" and bool(GROQ_API_KEY)


def require_groq_api_key() -> str:
    if can_use_groq():
        return GROQ_API_KEY

    raise RuntimeError(
        "GROQ_API_KEY is not set or LLM_PROVIDER is not 'groq'. Update backend/.env to enable Groq mode."
    )
