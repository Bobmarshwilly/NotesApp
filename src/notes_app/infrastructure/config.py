from typing import List, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """Класс с определением режима запуска приложения"""

    ENV_MODE: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class BaseConfig(BaseSettings):
    """Базовый класс конфигурации с общими настройками"""

    """Конфигурация базы данных"""
    ASYNC_DB_DRIVER: str = "postgresql+asyncpg"
    SYNC_DB_DRIVER: str = "postgresql"
    DB_PORT: str = "5432"
    DB_HOST: str

    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    """Конфигурация сервиса Kafka"""
    KAFKA_BOOTSTRAP_SERVERS: List[str]
    KAFKA_TOPIC_NAMES: Dict[str, str] = {"notes_events": "notes_events_topic"}
    KAFKA_PRODUCER_BASE: Dict[str, int | str] = {
        "client_id": "notes-app-producer",
        "acks": "all",
        "request_timeout_ms": 5000,
    }
    KAFKA_CONSUMER_BASE: Dict[str, str] = {
        "group_id": "my_consumer_group",
        "auto_offset_reset": "earliest",
    }

    """Конфигурация сервиса Redis"""
    REDIS_DRIVER: str = "redis"
    REDIS_PORT: str = "6379"
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRE_SECONDS: int = 3600
    REDIS_HOST: str

    @property
    def ASYNC_DB_URL(self) -> str:
        return f"{self.ASYNC_DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SYNC_DB_URL(self) -> str:
        return f"{self.SYNC_DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ALEMBIC_DB_URL(self) -> str:
        return f"{self.SYNC_DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def KAFKA_PRODUCER_CONFIG(self) -> dict:
        return {
            "bootstrap_servers": self.KAFKA_BOOTSTRAP_SERVERS,
            **self.KAFKA_PRODUCER_BASE,
        }

    @property
    def KAFKA_CONSUMER_CONFIG(self) -> dict:
        return {
            "bootstrap_servers": self.KAFKA_BOOTSTRAP_SERVERS,
            **self.KAFKA_CONSUMER_BASE,
        }

    @property
    def REDIS_URL(self) -> str:
        return f"{self.REDIS_DRIVER}://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"{self.REDIS_DRIVER}://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"{self.REDIS_DRIVER}://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class DevelopmentConfig(BaseConfig):
    DB_HOST: str = "localhost"
    KAFKA_BOOTSTRAP_SERVERS: List[str] = ["localhost:9092"]
    REDIS_HOST: str = "localhost"


class DockerConfig(BaseConfig):
    DB_HOST: str = "postgres"
    KAFKA_BOOTSTRAP_SERVERS: List[str] = ["kafka:9092"]
    REDIS_HOST: str = "redis"


def get_config() -> BaseConfig:
    env_config = EnvConfig()
    env_mode = env_config.ENV_MODE

    if env_mode == "development":
        return DevelopmentConfig()
    elif env_mode == "docker":
        return DockerConfig()
    else:
        raise ValueError(f"Unknown ENV_MODE: {env_mode}")


config = get_config()
