from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_host: str = Field(
        default="localhost",
        title="DB_HOST",
        description="Database hostname",
    )
    db_name: str = Field(
        default="test",
        title="DB_NAME",
        description="Database name",
    )
    db_username: str = Field(
        default="admin",
        title="DB_USERNAME",
        description="Database username",
    )
    db_password: str = Field(
        default="password",
        title="DB_PASSWORD",
        description="Database password",
    )
    db_port: str = Field(
        default="5432",
        title="DB_PORT",
        description="Database db_port",
    )
    secret_key: str = Field(
        default="",
        title="SECRET_KEY",
        description="Secret key for password hashing",
    )
    hashing_algorithm: str = Field(
        default="",
        title="HASHING_ALGORITHM",
        description="Password hashing algorithm",
    )
    access_token_expiry: str = Field(
        default="10",
        title="ACCESS_TOKEN_EXPIRY",
        description="Access token expiry in minutes",
    )
    admin_mail: str = Field(
        default="",
        title="ADMIN_MAIL",
        description="Administrator mail address",
    )
    admin_username: str = Field(
        default="",
        title="ADMIN_USERNAME",
        description="Administrator username",
    )
    admin_password: str = Field(
        default="",
        title="ADMIN_PASSWORD",
        description="Administrator password",
    )
    name_length: int = Field(
        default=32,
        title="NAME_LENGTH",
        description="Name column length",
    )
    email_length: int = Field(
        default=256,
        title="EMAIL_LENGTH",
        description="Email column length",
    )
    password_hash_length: int = Field(
        default=72,
        title="PASSWORD_HASH_LENGTH",
        description="Password column length",
    )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
