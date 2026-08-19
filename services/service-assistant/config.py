from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "service-assistant"
    app_version: str = "1.0.0"

    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str

    groq_api_key: str

    groq_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()