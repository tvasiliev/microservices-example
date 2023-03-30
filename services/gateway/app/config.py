from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""

    PROJECT_NAME = "Gateway Service"


config = Config()
