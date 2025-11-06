"""
FastAPI application configuration using Pydantic Settings
"""
from typing import List, Set
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with automatic environment variable loading"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App Configuration
    app_name: str = "test.me API"
    environment: str = Field(default="development", alias="FLASK_ENV")
    debug: bool = True
    secret_key: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=5000, alias="PORT")
    
    # File Upload
    max_file_size: int = Field(default=16777216, alias="MAX_FILE_SIZE")  # 16MB
    allowed_extensions: Set[str] = {"pdf"}
    
    # Firebase (Backend Admin SDK)
    firebase_credentials_path: str = Field(default="serviceAccountKey.json", alias="FIREBASE_CREDENTIALS_PATH")
    firebase_storage_bucket: str = Field(alias="FIREBASE_STORAGE_BUCKET")
    
    # Firebase (Web SDK for Admin OAuth)
    firebase_api_key: str | None = Field(default=None, alias="FIREBASE_API_KEY")
    firebase_auth_domain: str | None = Field(default=None, alias="FIREBASE_AUTH_DOMAIN")
    firebase_project_id: str | None = Field(default=None, alias="FIREBASE_PROJECT_ID")
    
    # AI Services
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5", alias="OPENAI_MODEL")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    google_model: str = Field(default="gemini-1.5-pro", alias="GOOGLE_MODEL")
    default_ai_provider: str = Field(default="gpt", alias="DEFAULT_AI_PROVIDER")
    
    # Admin Authentication
    admin_id: str = Field(default="admin", alias="ADMIN_ID")
    admin_pw: str = Field(default="admin", alias="ADMIN_PW")
    
    # CORS
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()

