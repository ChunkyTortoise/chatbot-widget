from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://chatbot:chatbot@localhost:5432/chatbot_widget"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    admin_key: str = "dev-admin-key"
    secret_key: str = "dev-secret-key"
    environment: str = "development"

    # Widget defaults
    default_system_prompt: str = (
        "You are a helpful assistant. Answer questions concisely and helpfully "
        "based on the provided context. If you don't know something, say so."
    )

    # RAG settings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    retrieval_top_k: int = 5
    chunk_size: int = 400
    chunk_overlap: int = 50


settings = Settings()
