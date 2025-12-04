"""Tests for LLM configuration via settings."""
import os
import pytest
from unittest.mock import patch


class TestConfig:
    """Test suite for Settings configuration."""
    
    def test_default_values(self):
        """Test that default values load correctly without .env file."""
        # Import fresh settings
        from backend.config import Settings
        settings = Settings()
        
        # Check default provider
        assert settings.DEFAULT_MODEL_PROVIDER == "gemini"
        assert settings.DEFAULT_SEARCH_PROVIDER == "ddg"
        
        # Check default model names
        assert settings.OPENAI_MODEL == "gpt-5-nano"
        assert settings.GEMINI_MODEL == "gemini-2.5-flash"
        assert settings.GROK_MODEL == "grok-4-1-fast"
        
        # Check default temperatures
        assert settings.OPENAI_TEMPERATURE == 1.0
        assert settings.GEMINI_TEMPERATURE == 0.7
        assert settings.GROK_TEMPERATURE == 0.8
    
    def test_get_provider_config_openai(self):
        """Test get_provider_config returns correct OpenAI config."""
        from backend.config import settings
        
        config = settings.get_provider_config("openai")
        
        assert "model" in config
        assert "temperature" in config
        assert "max_tokens" in config
        assert config["model"] == settings.OPENAI_MODEL
        assert config["temperature"] == settings.OPENAI_TEMPERATURE
    
    def test_get_provider_config_gemini(self):
        """Test get_provider_config returns correct Gemini config."""
        from backend.config import settings
        
        config = settings.get_provider_config("gemini")
        
        assert config["model"] == settings.GEMINI_MODEL
        assert config["temperature"] == settings.GEMINI_TEMPERATURE
    
    def test_get_provider_config_grok(self):
        """Test get_provider_config returns correct Grok config."""
        from backend.config import settings
        
        config = settings.get_provider_config("grok")
        
        assert config["model"] == settings.GROK_MODEL
        assert config["temperature"] == settings.GROK_TEMPERATURE
    
    def test_get_provider_config_unknown_falls_back_to_gemini(self):
        """Test that unknown provider falls back to Gemini config."""
        from backend.config import settings
        
        config = settings.get_provider_config("unknown_provider")
        
        assert config["model"] == settings.GEMINI_MODEL
    
    def test_environment_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {
            "DEFAULT_MODEL_PROVIDER": "openai",
            "OPENAI_MODEL": "gpt-4-turbo",
            "OPENAI_TEMPERATURE": "0.5"
        }):
            from backend.config import Settings
            settings = Settings()
            
            assert settings.DEFAULT_MODEL_PROVIDER == "openai"
            assert settings.OPENAI_MODEL == "gpt-4-turbo"
            assert settings.OPENAI_TEMPERATURE == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
