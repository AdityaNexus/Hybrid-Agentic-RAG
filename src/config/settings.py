from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_base_url: str = "http://localhost:8080/v1"
    llm_api_key: str = "local"
    llm_model: str = "Qwen3-1.7B-Q8_0.gguf"
    llm_enable_thinking: bool = False

    data_dir: str = "data"
    documents_dir: str = "data/documents"
    chroma_dir: str = "data/chroma"
    graph_dir: str = "data/graph"
    cache_dir: str = "data/cache"
    state_dir: str = "data/state"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()