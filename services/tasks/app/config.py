import os

from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""

    PROJECT_NAME = "Tasks Service"
    RABBITMQ_URL = os.environ.get("RMQ_URL")


config = Config()
