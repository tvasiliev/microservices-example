import os

from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""

    PROJECT_NAME = "Tasks Service"
    POSTGRES_URL: str = os.environ.get("PG_URL")
    RABBITMQ_URL = os.environ.get("RMQ_URL")
    CLIENT_PUBLISH_RETRIES: int = 5
    SERVER_PUBLISH_RETRIES: int = 5


config = Config()
