
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "Lenny Growth Assistant")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        self.llm_provider = os.getenv(
            "LLM_PROVIDER_TOGGLE", "local"
        ).strip().lower()

        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

        self.ollama_base_url = os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        ).rstrip("/")

        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant",
        )

        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )

        self.retrieval_top_k = int(os.getenv("RETRIEVAL_TOP_K", "5"))
        self.frontend_origin = os.getenv(
            "FRONTEND_ORIGIN", "http://localhost:5173"
        )

        if self.llm_provider not in {"local", "cloud"}:
            raise ValueError(
                "LLM_PROVIDER_TOGGLE must be 'local' or 'cloud'."
            )

        if self.retrieval_top_k < 1:
            raise ValueError("RETRIEVAL_TOP_K must be at least 1.")




@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
