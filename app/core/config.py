import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Organizations Directory API"
    api_v1_prefix: str = "/api/v1"
    api_key: str = Field(default=os.getenv("API_KEY", "secret-key"))

    # Database
    database_url: str = Field(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@db:5432/secunda_orgs",
        )
    )

    class Config:
        env_file = ".env"


settings = Settings()


