"""Configuration management module.

Loads configuration from environment variables using pydantic-settings.
Supports both local and cloud deployment modes.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Deployment mode: local | cloud
    DEPLOYMENT: str = "local"

    # ===========================================
    # Database configuration (auto-selected by DEPLOYMENT)
    # ===========================================
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "quant"

    # ===========================================
    # Redis configuration (auto-selected by DEPLOYMENT)
    # ===========================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # ===========================================
    # Local development settings
    # ===========================================
    LOCAL_DB_HOST: str = "localhost"
    LOCAL_DB_PORT: int = 3306
    LOCAL_DB_USER: str = "root"
    LOCAL_DB_PASSWORD: str = "quant2026"
    LOCAL_DB_NAME: str = "quant"

    LOCAL_REDIS_HOST: str = "localhost"
    LOCAL_REDIS_PORT: int = 6379
    LOCAL_REDIS_PASSWORD: str = ""

    # ===========================================
    # Cloud server settings
    # ===========================================
    CLOUD_HOST: str = ""  # 云服务器 IP，从 .env CLOUD_HOST 读取
    CLOUD_DB_HOST: str = ""  # 默认同 CLOUD_HOST
    CLOUD_DB_PORT: int = 3306
    CLOUD_DB_USER: str = "root"
    CLOUD_DB_PASSWORD: str = "quant2026"
    CLOUD_DB_NAME: str = "quant"

    CLOUD_REDIS_HOST: str = ""  # 默认同 CLOUD_HOST
    CLOUD_REDIS_PORT: int = 6379
    CLOUD_REDIS_PASSWORD: str = ""

    # ===========================================
    # API configuration
    # ===========================================
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_PORT: int = 3000

    # ===========================================
    # Security configuration
    # ===========================================
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # ===========================================
    # Data source configuration
    # ===========================================
    DATA_SOURCE: str = "akshare"
    TUSHARE_TOKEN: str = ""

    # ===========================================
    # QMT configuration
    # ===========================================
    QMT_HOST: str = "localhost"
    QMT_PORT: int = 58610
    QMT_USER: str = ""
    QMT_PASSWORD: str = ""

    @property
    def db_host(self) -> str:
        """Get database host based on deployment mode."""
        if self.DEPLOYMENT == "cloud":
            return self.CLOUD_DB_HOST or self.CLOUD_HOST
        return self.LOCAL_DB_HOST

    @property
    def db_port(self) -> int:
        """Get database port based on deployment mode."""
        return self.CLOUD_DB_PORT if self.DEPLOYMENT == "cloud" else self.LOCAL_DB_PORT

    @property
    def db_user(self) -> str:
        """Get database user based on deployment mode."""
        return self.CLOUD_DB_USER if self.DEPLOYMENT == "cloud" else self.LOCAL_DB_USER

    @property
    def db_password(self) -> str:
        """Get database password based on deployment mode."""
        return self.CLOUD_DB_PASSWORD if self.DEPLOYMENT == "cloud" else self.LOCAL_DB_PASSWORD

    @property
    def db_name(self) -> str:
        """Get database name based on deployment mode."""
        return self.CLOUD_DB_NAME if self.DEPLOYMENT == "cloud" else self.LOCAL_DB_NAME

    @property
    def redis_host(self) -> str:
        """Get Redis host based on deployment mode."""
        if self.DEPLOYMENT == "cloud":
            return self.CLOUD_REDIS_HOST or self.CLOUD_HOST
        return self.LOCAL_REDIS_HOST

    @property
    def redis_port(self) -> int:
        """Get Redis port based on deployment mode."""
        return self.CLOUD_REDIS_PORT if self.DEPLOYMENT == "cloud" else self.LOCAL_REDIS_PORT

    @property
    def redis_password(self) -> str:
        """Get Redis password based on deployment mode."""
        return self.CLOUD_REDIS_PASSWORD if self.DEPLOYMENT == "cloud" else self.LOCAL_REDIS_PASSWORD

    @property
    def database_url(self) -> str:
        """Generate async database URL for SQLAlchemy."""
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def sync_database_url(self) -> str:
        """Generate sync database URL for SQLAlchemy."""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def redis_url(self) -> str:
        """Generate Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.REDIS_DB}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.REDIS_DB}"


# Global settings instance
settings = Settings()
