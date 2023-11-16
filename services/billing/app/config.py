import os

from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""

    PROJECT_NAME = "Billing Service"
    QUEUE_NAME = "billing"
    RABBITMQ_URL = os.environ.get("RMQ_URL")


config = Config()
