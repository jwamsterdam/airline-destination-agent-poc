from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Airline Destination Agent API"
    environment: str = "development"
    database_url: str = "sqlite:///./airline_agent.db"
    graphql_endpoint_url: str = "http://127.0.0.1:8000/graphql"
    agent_default_limit: int = 5
    agent_use_llm: bool = True
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
