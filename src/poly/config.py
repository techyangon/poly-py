from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    access_token_audience: str = Field(
        ...,
        title="ACCESS_TOKEN_AUDIENCE",
        description="Access token audience",
    )
    access_token_expiry: int = Field(
        default=10,
        title="ACCESS_TOKEN_EXPIRY",
        description="Access token expiry in minutes",
    )
    access_token_issuer: str = Field(
        ...,
        title="ACCESS_TOKEN_ISSUER",
        description="Access token issuer",
    )
    admin_mail: str = Field(
        ...,
        title="ADMIN_MAIL",
        description="Administrator mail address",
    )
    admin_password: str = Field(
        ...,
        title="ADMIN_PASSWORD",
        description="Administrator password",
    )
    admin_username: str = Field(
        ...,
        title="ADMIN_USERNAME",
        description="Administrator username",
    )
    db_host: str = Field(
        ...,
        title="DB_HOST",
        description="Database hostname",
    )
    db_name: str = Field(
        ...,
        title="DB_NAME",
        description="Database name",
    )
    db_password: str = Field(
        ...,
        title="DB_PASSWORD",
        description="Database password",
    )
    db_port: str = Field(
        ...,
        title="DB_PORT",
        description="Database db_port",
    )
    db_username: str = Field(
        ...,
        title="DB_USERNAME",
        description="Database username",
    )
    email_length: int = Field(
        default=256,
        title="EMAIL_LENGTH",
        description="Email column length",
    )
    hashing_algorithm: str = Field(
        default="HS256",
        title="HASHING_ALGORITHM",
        description="Password hashing algorithm",
    )
    name_length: int = Field(
        default=32,
        title="NAME_LENGTH",
        description="Name column length",
    )
    password_hash_length: int = Field(
        default=72,
        title="PASSWORD_HASH_LENGTH",
        description="Password column length",
    )
    refresh_token_expiry: int = Field(
        default=60,
        title="REFRESH_TOKEN_EXPIRY",
        description="Refresh token expiry in minutes",
    )
    secret_key: str = Field(
        ...,
        title="SECRET_KEY",
        description="Secret for hashing access token",
    )


settings = Settings()  # pyright: ignore
