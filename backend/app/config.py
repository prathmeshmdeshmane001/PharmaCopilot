import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    app_name: str = "PharmaCopilot API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    
    # API Keys (Optional - mock mode fallback used if absent or unreachable)
    gemini_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "auto"  # "auto", "gemini", "openai", or "mock"
    
    # CORS
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Upload limits
    max_upload_size_mb: int = 10

settings = Settings()
