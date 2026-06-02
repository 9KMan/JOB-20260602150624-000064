"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/psd_dev",
        description="PostgreSQL database connection URL",
    )
    db_pool_size: int = Field(default=5, ge=1, le=100)
    db_max_overflow: int = Field(default=10, ge=0, le=100)
    db_pool_timeout: int = Field(default=30, ge=1)
    db_pool_recycle: int = Field(default=3600, ge=0)
    db_echo: bool = Field(default=False)

    model_config = SettingsConfigDict(env_prefix="DB_")


class RedisSettings(BaseSettings):
    """Redis configuration settings."""

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_max_connections: int = Field(default=50, ge=1)

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class AuthSettings(BaseSettings):
    """Authentication and JWT settings."""

    auth0_domain: str = Field(
        default="",
        description="Auth0 domain",
    )
    auth0_audience: str = Field(
        default="",
        description="Auth0 audience identifier",
    )
    auth0_algorithms: list[str] = Field(default=["RS256"])
    jwt_secret_key: str = Field(
        default="",
        description="JWT secret key for HS256 algorithm",
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1)
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1)

    @field_validator("auth0_algorithms", mode="before")
    @classmethod
    def parse_algorithms(cls, v: Any) -> list[str]:
        """Parse algorithms from comma-separated string."""
        if isinstance(v, str):
            return [a.strip() for a in v.split(",")]
        return v

    model_config = SettingsConfigDict(env_prefix="AUTH0_")


class YotiSettings(BaseSettings):
    """Yoti age verification settings."""

    yoti_client_sdk_id: str = Field(default="", description="Yoti Client SDK ID")
    yoti_pem_file: str = Field(default="", description="Path to Yoti PEM file")

    model_config = SettingsConfigDict(env_prefix="YOTI_")


class BlueCheckSettings(BaseSettings):
    """BlueCheck age verification settings."""

    bluecheck_api_key: str = Field(default="", description="BlueCheck API key")
    bluecheck_api_url: str = Field(
        default="https://api.bluecheck.com.au",
        description="BlueCheck API URL",
    )

    model_config = SettingsConfigDict(env_prefix="BLUECHECK_")


class OndatoSettings(BaseSettings):
    """Ondato identity verification settings."""

    ondato_username: str = Field(default="", description="Ondato API username")
    ondato_password: str = Field(default="", description="Ondato API password")
    ondato_organization_id: str = Field(default="", description="Ondato Organization ID")
    ondato_api_url: str = Field(
        default="https://api.ondato.com",
        description="Ondato API URL",
    )

    model_config = SettingsConfigDict(env_prefix="ONDATO_")


class CCBillSettings(BaseSettings):
    """CCBill payment processing settings."""

    ccbill_account_number: str = Field(
        default="",
        description="CCBill account number",
    )
    ccbill_sub_account_number: str = Field(
        default="",
        description="CCBill sub-account number",
    )
    ccbill_salt: str = Field(default="", description="CCBill salt for webhook verification")
    ccbill_flexid: str = Field(default="", description="CCBill Flex ID")
    ccbill_salt_key: str = Field(default="", description="CCBill salt key")
    ccbill_dataform_salt: str = Field(default="", description="CCBill dataform salt")
    ccbill_api_url: str = Field(
        default="https://api.ccbill.com",
        description="CCBill API URL",
    )

    model_config = SettingsConfigDict(env_prefix="CCBILL_")


class PaxumSettings(BaseSettings):
    """Paxum payment processing settings."""

    paxum_api_key: str = Field(default="", description="Paxum API key")
    paxum_api_url: str = Field(
        default="https://api.paxum.com",
        description="Paxum API URL",
    )

    model_config = SettingsConfigDict(env_prefix="PAXUM_")


class PipedriveSettings(BaseSettings):
    """Pipedrive CRM settings."""

    pipedrive_api_token: str = Field(default="", description="Pipedrive API token")
    pipedrive_api_url: str = Field(
        default="https://api.pipedrive.com",
        description="Pipedrive API URL",
    )

    model_config = SettingsConfigDict(env_prefix="PIPEDRIVE_")


class HubSpotSettings(BaseSettings):
    """HubSpot CRM settings."""

    hubspot_api_key: str = Field(default="", description="HubSpot API key")
    hubspot_api_url: str = Field(
        default="https://api.hubapi.com",
        description="HubSpot API URL",
    )

    model_config = SettingsConfigDict(env_prefix="HUBSPOT_")


class MauticSettings(BaseSettings):
    """Mautic marketing automation settings."""

    mautic_url: str = Field(default="", description="Mautic instance URL")
    mautic_username: str = Field(default="", description="Mautic username")
    mautic_password: str = Field(default="", description="Mautic password")

    model_config = SettingsConfigDict(env_prefix="MAUTIC_")


class AWSSettings(BaseSettings):
    """AWS configuration settings."""

    aws_access_key_id: str = Field(default="", description="AWS access key ID")
    aws_secret_access_key: str = Field(default="", description="AWS secret access key")
    aws_region: str = Field(default="us-east-1", description="AWS region")
    s3_bucket: str = Field(default="", description="S3 bucket name")
    aws_ses_from_email: str = Field(
        default="noreply@example.com",
        description="SES from email address",
    )

    model_config = SettingsConfigDict(env_prefix="AWS_")


class CelerySettings(BaseSettings):
    """Celery configuration settings."""

    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend URL",
    )

    model_config = SettingsConfigDict(env_prefix="CELERY_")


class AppSettings(BaseSettings):
    """Main application settings."""

    app_name: str = Field(default="Premium Service Directory")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development", description="Deployment environment")
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False)
    secret_key: str = Field(
        default="change-me-in-production",
        description="Application secret key",
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins",
    )
    rate_limit_per_minute: int = Field(default=60, ge=1, description="API rate limit")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(env_prefix="")


class Settings(BaseSettings):
    """Combined application settings."""

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    yoti: YotiSettings = Field(default_factory=YotiSettings)
    bluecheck: BlueCheckSettings = Field(default_factory=BlueCheckSettings)
    ondato: OndatoSettings = Field(default_factory=OndatoSettings)
    ccbill: CCBillSettings = Field(default_factory=CCBillSettings)
    paxum: PaxumSettings = Field(default_factory=PaxumSettings)
    pipedrive: PipedriveSettings = Field(default_factory=PipedriveSettings)
    hubspot: HubSpotSettings = Field(default_factory=HubSpotSettings)
    mautic: MauticSettings = Field(default_factory=MauticSettings)
    aws: AWSSettings = Field(default_factory=AWSSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()