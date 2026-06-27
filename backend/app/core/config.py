import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

DEMO_SECRET_KEY = "change-me-local-demo-secret-32-bytes-minimum"
LOCAL_ENVS = {"local", "demo", "development", "test"}


def _get_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _get_str(name: str, default: str) -> str:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = _get_str("APP_NAME", "Annuaire Artisans BF API")
    APP_ENV: str = _get_str("APP_ENV", "local")
    DEMO_MODE: bool = _get_bool("DEMO_MODE", True)
    SECRET_KEY: str = _get_str("SECRET_KEY", DEMO_SECRET_KEY)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = _get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    DATABASE_URL: str = _get_str("DATABASE_URL", "sqlite:///./annuaire_artisans.db")
    UPLOAD_DIR: str = _get_str("UPLOAD_DIR", "uploads")
    MAX_PHOTOS_PER_BUSINESS: int = _get_int("MAX_PHOTOS_PER_BUSINESS", 3)
    MAX_UPLOAD_SIZE_MB: int = _get_int("MAX_UPLOAD_SIZE_MB", 5)
    OLLAMA_HOST: str = _get_str("OLLAMA_HOST", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = _get_str("OLLAMA_MODEL", "llama3.1:8b")

    def __post_init__(self) -> None:
        app_env = self.APP_ENV.strip().lower()
        if self.SECRET_KEY == DEMO_SECRET_KEY and app_env not in LOCAL_ENVS:
            raise RuntimeError("SECRET_KEY must be changed outside local/demo/test environments")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
            raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0")
        if self.MAX_PHOTOS_PER_BUSINESS <= 0:
            raise RuntimeError("MAX_PHOTOS_PER_BUSINESS must be greater than 0")
        if self.MAX_UPLOAD_SIZE_MB <= 0:
            raise RuntimeError("MAX_UPLOAD_SIZE_MB must be greater than 0")


settings = Settings()
