from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""

    PROJECT_NAME = "Billing Service"


config = Config()
