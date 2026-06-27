import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

APP_NAME = os.getenv("APP_NAME", "Annuaire Artisans BF - Module Membre 3")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./membre3_data.db")

# Si la DB SQLite est donnée en chemin relatif, elle sera créée dans backend/.
if DATABASE_URL.startswith("sqlite:///./"):
    db_name = DATABASE_URL.replace("sqlite:///./", "")
    DATABASE_URL = f"sqlite:///{BASE_DIR / db_name}"

OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
