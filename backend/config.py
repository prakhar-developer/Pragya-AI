import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_CURRENT_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _CURRENT_DIR.parent
_ENV_FILES = [str(_CURRENT_DIR / ".env"), str(_ROOT_DIR / ".env")]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        extra="ignore",
    )

    APP_NAME: str = "PRAGYA AI Industrial Knowledge Reasoning Engine"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS origins
    ALLOWED_ORIGINS: Union[List[str], str] = ["*"]

    # Neo4j Settings (Optional in demo/fallback mode)
    NEO4J_URI: str = ""
    NEO4J_PASSWORD: str = ""
    NEO4J_USER: str = "neo4j"

    # Supabase Settings (Optional in demo/fallback mode)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Groq Settings (Optional in demo/fallback mode)
    GROQ_API_KEY: str = ""

    # Models
    GROQ_TEXT_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_VISION_MODEL: str = "llama-3.2-11b-vision-preview"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Demo / Fallback Mode (auto-enabled if cloud keys are absent)
    DEMO_MODE: bool = False

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if not v or v == "*":
            return ["*"]
        if isinstance(v, str):
            cleaned = v.strip("[]'\" ")
            items = [item.strip(" '\"\t\r\n") for item in cleaned.split(",") if item.strip(" '\"\t\r\n")]
            return items if items else ["*"]
        if isinstance(v, (list, tuple)):
            return [str(item).strip() for item in v if item]
        return ["*"]

    @property
    def is_demo_mode(self) -> bool:
        return self.DEMO_MODE or not bool(
            self.SUPABASE_URL and self.SUPABASE_KEY and self.GROQ_API_KEY
        )


settings = Settings()

