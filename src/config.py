"""
Configuration management for RAG systems
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4-turbo-preview"
    openai_fast_model: str = "gpt-3.5-turbo"

    # Vector Store Configuration
    vector_store_path: str = "data/vector_store"
    collection_name: str = "customer_support_kb"

    # Retrieval Configuration
    default_top_k: int = 10
    rerank_top_k: int = 3

    # Generation Configuration
    max_tokens: int = 1000
    temperature: float = 0.1

    # Project Paths
    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def knowledge_base_dir(self) -> Path:
        return self.data_dir / "knowledge_base"

    @property
    def vector_store_dir(self) -> Path:
        return self.project_root / self.vector_store_path

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment"""
    api_key = settings.openai_api_key
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return api_key
