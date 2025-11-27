"""
Application Configuration Module

This module contains all configuration settings for the GazTracker application.
It uses pydantic-settings for environment variable management and validation.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=None,  # Don't read .env files - use environment variables only
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # =============================================================================
    # Application Configuration
    # =============================================================================
    APP_NAME: str = Field(default="GazTracker", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_ENVIRONMENT: str = Field(default="development", description="Environment (development/staging/production)")
    DEBUG: bool = Field(default=True, description="Debug mode")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")

    # =============================================================================
    # Server Configuration
    # =============================================================================
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # =============================================================================
    # Database Configuration (PostgreSQL)
    # =============================================================================
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="gaztracker_db", description="PostgreSQL database name")
    POSTGRES_USER: str = Field(default="gaztracker_user", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="", description="PostgreSQL password")

    DATABASE_URL: Optional[str] = Field(default=None, description="Complete database URL")

    # Connection Pool Settings
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Connection recycle time in seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL queries")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        """
        Construct DATABASE_URL from individual components if not provided.
        """
        if v:
            return v

        values = info.data
        return (
            f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_HOST')}:"
            f"{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
        )

    # =============================================================================
    # Redis Configuration
    # =============================================================================
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_URL: Optional[str] = Field(default=None, description="Complete Redis URL")

    # Redis Connection Settings
    REDIS_MAX_CONNECTIONS: int = Field(default=50, description="Max Redis connections")
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, description="Redis socket timeout")
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(default=5, description="Redis connect timeout")

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Optional[str], info) -> str:
        """
        Construct REDIS_URL from individual components if not provided.
        """
        if v:
            return v

        values = info.data
        password = values.get('REDIS_PASSWORD')
        auth = f":{password}@" if password else ""

        return (
            f"redis://{auth}{values.get('REDIS_HOST')}:"
            f"{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
        )

    # =============================================================================
    # JWT & Security Configuration
    # =============================================================================
    SECRET_KEY: str = Field(
        default="your_super_secret_key_min_32_chars_change_this_in_production",
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration (minutes)")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=10080, description="Refresh token expiration (minutes)")
    BCRYPT_ROUNDS: int = Field(default=12, description="BCrypt hashing rounds")

    # =============================================================================
    # CORS Configuration
    # =============================================================================
    ALLOWED_ORIGINS: Union[str, List[str]] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:8082"],
        description="Allowed CORS origins"
    )
    ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS")
    ALLOWED_METHODS: Union[str, List[str]] = Field(default=["*"], description="Allowed HTTP methods")
    ALLOWED_HEADERS: Union[str, List[str]] = Field(default=["*"], description="Allowed HTTP headers")

    @field_validator("ALLOWED_ORIGINS", "ALLOWED_METHODS", "ALLOWED_HEADERS", mode="after")
    @classmethod
    def parse_cors_list(cls, v) -> List[str]:
        """Parse CORS lists from string or list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # =============================================================================
    # Logging Configuration
    # =============================================================================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json/text)")
    LOG_FILE_PATH: str = Field(default="logs/gaztracker.log", description="Log file path")
    LOG_MAX_SIZE: int = Field(default=10485760, description="Max log file size (bytes)")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Number of log backups")

    # =============================================================================
    # Twilio Configuration (SMS Notifications)
    # =============================================================================
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, description="Twilio account SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, description="Twilio auth token")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, description="Twilio phone number")

    # =============================================================================
    # Email Configuration (SMTP)
    # =============================================================================
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_FROM_EMAIL: str = Field(default="noreply@gaztracker.com", description="From email address")
    SMTP_FROM_NAME: str = Field(default="GazTracker System", description="From name")
    SMTP_TLS: bool = Field(default=True, description="Use TLS")
    SMTP_SSL: bool = Field(default=False, description="Use SSL")

    # =============================================================================
    # Notification Settings
    # =============================================================================
    ENABLE_EMAIL_NOTIFICATIONS: bool = Field(default=True, description="Enable email notifications")
    ENABLE_SMS_NOTIFICATIONS: bool = Field(default=False, description="Enable SMS notifications")
    NOTIFICATION_RETRY_ATTEMPTS: int = Field(default=3, description="Notification retry attempts")
    NOTIFICATION_RETRY_DELAY: int = Field(default=60, description="Retry delay in seconds")

    # =============================================================================
    # Business Rules Configuration
    # =============================================================================
    DELIVERY_DELAY_ALERT_HOURS: int = Field(default=48, description="Delivery delay alert threshold (hours)")
    OTP_EXPIRY_MINUTES: int = Field(default=15, description="OTP expiration time (minutes)")
    MAX_GEOLOCATION_DISTANCE_KM: float = Field(default=5.0, description="Max geolocation distance (km)")

    # =============================================================================
    # RFID Configuration
    # =============================================================================
    RFID_TAG_PREFIX: str = Field(default="GAZ", description="RFID tag prefix")
    RFID_TAG_LENGTH: int = Field(default=12, description="RFID tag length")

    # =============================================================================
    # Pagination Defaults
    # =============================================================================
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default pagination page size")
    MAX_PAGE_SIZE: int = Field(default=100, description="Maximum page size")

    # =============================================================================
    # File Upload Configuration
    # =============================================================================
    MAX_UPLOAD_SIZE: int = Field(default=10485760, description="Max upload size (bytes)")
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".jpg", ".jpeg", ".png"],
        description="Allowed file extensions"
    )
    UPLOAD_DIR: str = Field(default="uploads/", description="Upload directory")

    @field_validator("ALLOWED_UPLOAD_EXTENSIONS", mode="before")
    @classmethod
    def parse_extensions(cls, v) -> List[str]:
        """Parse file extensions from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    # =============================================================================
    # Rate Limiting
    # =============================================================================
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")

    # =============================================================================
    # Monitoring & Metrics
    # =============================================================================
    ENABLE_PROMETHEUS: bool = Field(default=False, description="Enable Prometheus metrics")
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus port")

    # =============================================================================
    # External Services
    # =============================================================================
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, description="Google Maps API key")

    # =============================================================================
    # Testing Configuration
    # =============================================================================
    TEST_DATABASE_URL: Optional[str] = Field(default=None, description="Test database URL")
    TEST_REDIS_URL: Optional[str] = Field(default=None, description="Test Redis URL")

    # =============================================================================
    # Feature Flags
    # =============================================================================
    ENABLE_AUDIT_LOG: bool = Field(default=True, description="Enable audit logging")
    ENABLE_GEOLOCATION: bool = Field(default=True, description="Enable geolocation")
    ENABLE_AUTO_NOTIFICATIONS: bool = Field(default=True, description="Enable auto notifications")
    ENABLE_RATE_LIMITING: bool = Field(default=True, description="Enable rate limiting")

    # =============================================================================
    # Computed Properties
    # =============================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENVIRONMENT.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.APP_ENVIRONMENT.lower() == "testing"

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration dictionary.

        Returns:
            Dict[str, Any]: Logging configuration
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "json": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.LOG_LEVEL,
                    "formatter": "default" if self.LOG_FORMAT == "text" else "json",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.LOG_LEVEL,
                    "formatter": "json",
                    "filename": self.LOG_FILE_PATH,
                    "maxBytes": self.LOG_MAX_SIZE,
                    "backupCount": self.LOG_BACKUP_COUNT,
                },
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console", "file"] if not self.is_testing else ["console"],
            },
        }


# =============================================================================
# Global Settings Instance
# =============================================================================

# Create a singleton instance of settings
settings = Settings()


# =============================================================================
# Logging Setup
# =============================================================================

def setup_logging() -> None:
    """
    Configure application logging based on settings.
    """
    import logging.config

    config = settings.get_logging_config()
    logging.config.dictConfig(config)

    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={settings.LOG_LEVEL}, "
        f"format={settings.LOG_FORMAT}, environment={settings.APP_ENVIRONMENT}"
    )


# Initialize logging on module import
if not settings.is_testing:
    setup_logging()
