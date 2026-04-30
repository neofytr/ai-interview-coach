from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    openai_api_key: str = ""
    openai_base_url: str = ""
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    enable_rag: bool = True
    enable_web_search: bool = True
    verbose: bool = False
    log_level: str = "WARNING"


@lru_cache
def get_settings() -> Settings:
    return Settings()
