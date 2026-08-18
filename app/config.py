"""Configuration loading.

Config declares NAMES; values arrive at runtime from the environment. The same code
reads a local Windows-authentication connection and a managed cloud credential later,
without modification.

Startup fails loudly on invalid or incomplete configuration. It never starts with a
silently defaulted security-relevant value (CP-005 / safe-default rule).
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, validated at startup by Pydantic.

    Pydantic guards trust boundaries — configuration, request bodies, ingestion input.
    It is NOT used row-wise over event data; that would violate AC-MINING-PLACEMENT.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PROJECTONE_",
        extra="ignore",
    )

    env: str = Field(default="local", description="Deployment environment name")
    db_connection_string: str = Field(description="ODBC connection string; never hardcoded")
    db_server: str = Field(description="Database server or instance")
    db_name: str = Field(description="Database name")
    api_host: str = Field(default="127.0.0.1")
    api_port: int = Field(default=8000)
    log_level: str = Field(default="INFO")
