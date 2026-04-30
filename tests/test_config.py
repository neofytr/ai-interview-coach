import os
from unittest.mock import patch

from utils.config import Settings


class TestSettingsDefaults:
    def test_default_llm_model(self):
        settings = Settings(openai_api_key="test", _env_file=None)
        assert settings.llm_model == "gpt-4o-mini"

    def test_default_embedding_model(self):
        settings = Settings(openai_api_key="test", _env_file=None)
        assert settings.embedding_model == "text-embedding-3-small"

    def test_default_enable_rag(self):
        settings = Settings(openai_api_key="test", _env_file=None)
        assert settings.enable_rag is True

    def test_default_enable_web_search(self):
        settings = Settings(openai_api_key="test", _env_file=None)
        assert settings.enable_web_search is True

    def test_default_verbose(self):
        settings = Settings(openai_api_key="test", _env_file=None)
        assert settings.verbose is False

    def test_default_log_level(self):
        settings = Settings(openai_api_key="test", _env_file=None)
        assert settings.log_level == "WARNING"

    def test_default_api_key_empty(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
        settings = Settings(_env_file=None)
        assert settings.openai_api_key == ""

    def test_default_base_url_empty(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
        settings = Settings(_env_file=None)
        assert settings.openai_base_url == ""


class TestSettingsEnvOverride:
    def test_env_overrides_model(self):
        with patch.dict(os.environ, {"LLM_MODEL": "gpt-4o"}):
            settings = Settings()
            assert settings.llm_model == "gpt-4o"

    def test_env_overrides_api_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}):
            settings = Settings()
            assert settings.openai_api_key == "sk-test123"

    def test_env_overrides_verbose(self):
        with patch.dict(os.environ, {"VERBOSE": "true"}):
            settings = Settings()
            assert settings.verbose is True

    def test_env_overrides_enable_rag(self):
        with patch.dict(os.environ, {"ENABLE_RAG": "false"}):
            settings = Settings()
            assert settings.enable_rag is False

    def test_env_overrides_enable_web_search(self):
        with patch.dict(os.environ, {"ENABLE_WEB_SEARCH": "false"}):
            settings = Settings()
            assert settings.enable_web_search is False

    def test_env_overrides_embedding_model(self):
        with patch.dict(os.environ, {"EMBEDDING_MODEL": "text-embedding-ada-002"}):
            settings = Settings()
            assert settings.embedding_model == "text-embedding-ada-002"
