"""Configuration management for Dad Joke MCP Server."""

import logging
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "json"
    log_file: str = "logs/dad-joke-mcp.log"
    log_to_file: bool = False
    log_requests: bool = True
    log_responses: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def log_level_int(self) -> int:
        """Convert log level string to logging constant."""
        return getattr(logging, self.log_level)


# Global settings instance
settings = Settings()
