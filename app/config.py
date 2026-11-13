from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Erma Tour & Travel"
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/erma_tours"
    secret_key: str = "change-me"
    debug: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
