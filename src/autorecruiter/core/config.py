from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration."""

    environment: str = Field("development", description="Deployment environment name")
    vector_store_url: str | None = Field(
        default=None,
        description="Connection string for the vector database (e.g. Pinecone, Weaviate)",
    )
    knowledge_graph_url: str | None = Field(
        default=None, description="Endpoint for the knowledge graph service"
    )
    policy_engine_url: str | None = Field(
        default=None, description="Endpoint for policy/rules engine"
    )
    scheduler_api_key: str | None = Field(
        default=None, description="API key for calendar scheduling provider"
    )

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()  # type: ignore[call-arg]
