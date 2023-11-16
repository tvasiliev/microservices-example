import os

from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""

    PROJECT_NAME = "Tasks Service"
    QUEUE_NAME = "tasks"
    RABBITMQ_URL = os.environ.get("RMQ_URL")


config = Config()
