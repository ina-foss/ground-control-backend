"""
settings.py - Configuration settings for the Ground Control API application.

This module provides environment loading functionalities using `dotenv` and
manages structured application settings using Pydantic's `BaseSettings`.
It includes definitions for the database connection, application metadata,
and Azure OpenAI deployment details.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Manages configuration settings for the Ground Control API application.
    """

    # Base settings
    application: str = "Ground Control API"
    version: str = "1.0.0"
    description: str = (
        "Ground Control API designed for secure communication between clients and a backend system."
    )
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    ssl_cert_file: str = ""
    api_docs_path: str = "/docs"

    # Logs
    log_level: str = "info"
    debug: bool = False

    # Database settings
    db_server: str = "postgresql"
    db_hostname: str = "localhost"
    db_database: str = "ground_control_db"
    db_username: str = "postgres"
    db_password: str = ""
    db_port: int = 5432

    # SSO settings
    sso_url: str = "http://localhost:9080"
    sso_realm: str = "ground_control"
    sso_client_id: str = "internal"
    sso_client_secret: str = "internal"

    # CORS settings
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_expose_headers: list[str] = [
        "Authorization",
        "Link",
        "X-Total-Count",
        "Highlighted",
        "Content-Disposition",
    ]  # Field
    cors_allow_origins: list[str] = [
        "http://localhost",
        "http://localhost:3000",
    ]

    # Model configuration
    model_config = SettingsConfigDict(
        env_prefix="gc_",
        extra="ignore",
        dotenv_prefix="gc_",
        env_file=(".env", ".env.local", ".env.prod"),
    )

    def get_db_connection_string(self) -> str:
        """
        Constructs and returns the database connection string.
        """
        return f"{self.db_server}://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_database}"
