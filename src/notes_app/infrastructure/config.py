from typing import List

import os
from dotenv import load_dotenv


load_dotenv()


class BaseConfig:
    """Базовый класс конфигурации с общими настройками"""

    DB_DRIVER = "postgresql+asyncpg"
    SYNC_DB_DRIVER = "postgresql"
    DB_PORT = "5432"
    DB_HOST: str

    KAFKA_BOOTSTRAP_SERVERS: List[str]

    KAFKA_TOPIC_NAMES = {
        "notes_events": "notes_events_topic",
    }
    KAFKA_PRODUCER_BASE = {
        "client_id": "notes-app-producer",
        "acks": "all",
        "request_timeout_ms": 5000,
    }
    KAFKA_CONSUMER_BASE = {
        "group_id": "my_consumer_group",
        "auto_offset_reset": "earliest",
    }

    def __init__(self):
        self.DB_USER = os.getenv("DATABASE_USER")
        self.DB_PASS = os.getenv("DATABASE_PASS")
        self.DB_NAME = os.getenv("DATABASE_NAME")

    @property
    def DB_URL(self):
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ALEMBIC_DB_URL(self):
        return f"{self.SYNC_DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def KAFKA_PRODUCER_CONFIG(self):
        return {
            "bootstrap_servers": self.KAFKA_BOOTSTRAP_SERVERS,
            **self.KAFKA_PRODUCER_BASE,
        }

    @property
    def KAFKA_CONSUMER_CONFIG(self):
        return {
            "bootstrap_servers": self.KAFKA_BOOTSTRAP_SERVERS,
            **self.KAFKA_CONSUMER_BASE,
        }


class DevelopmentConfig(BaseConfig):
    """Конфигурация для разработки на локальном копмпьютере"""

    DB_HOST = "localhost"
    KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]


class DockerConfig(BaseConfig):
    """Конфигурация для сборки и запуска приложения в docker"""

    DB_HOST = "postgres"
    KAFKA_BOOTSTRAP_SERVERS = ["kafka:9092"]


status = os.getenv("ENVIRONMENT")
config: BaseConfig

if status == "development":
    config = DevelopmentConfig()
elif status == "docker":
    config = DockerConfig()
