from functools import lru_cache

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
        ...,
        title="ACCESS_TOKEN_EXPIRY",
        description="Access token expiry in minutes",
    )
    access_token_issuer: str = Field(
        ...,
        title="ACCESS_TOKEN_ISSUER",
        description="Access token issuer",
    )
    address_length: int = Field(
        ...,
        title="ADDRESS_LENGTH",
        description="Physical address",
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
        ...,
        title="REFRESH_TOKEN_EXPIRY",
        description="Refresh token expiry in minutes",
    )
    secret_key: str = Field(
        ...,
        title="SECRET_KEY",
        description="Secret for hashing access token",
    )
    townships_file: str = Field(
        "",
        title="TOWNSHIPS_FILE",
        description="CSV file for townships data",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


@lru_cache
def get_rbac_models() -> str:
    return """
        [request_definition]
        r = sub, obj, act

        [policy_definition]
        p = sub, obj, act

        [role_definition]
        g = _, _

        [policy_effect]
        e = some(where (p.eft == allow))

        [matchers]
        m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
    """
