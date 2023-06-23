from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_host: str = Field(
        default="localhost", title="DB_HOST", description="Database hostname"
    )
    db_name: str = Field(default="test", title="DB_NAME", description="Database name")
    db_username: str = Field(
        default="admin", title="DB_USERNAME", description="Database username"
    )
    db_password: str = Field(
        default="password", title="DB_PASSWORD", description="Database password"
    )
    db_port: str = Field(default="5432", title="DB_PORT", description="Database port")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
