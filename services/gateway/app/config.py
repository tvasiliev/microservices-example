import os

from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""

    PROJECT_NAME = "auth service"
    POSTGRES_URL: str = os.environ.get("PG_URL")


class JWTConfig(BaseSettings):
    """fastapi-jwt-auth configuration"""

    authjwt_algorithm: str = "RS512"
    authjwt_private_key: str = os.environ.get("JWT_PRIVATE_KEY")
    authjwt_public_key: str = os.environ.get("JWT_PUBLIC_KEY")
    authjwt_secret_key: str = os.environ.get("JWT_SECRET_KEY")
    authjwt_token_location: set = {"cookies"}
    authjwt_denylist_enabled: bool = True
    authjwt_cookie_secure: bool = False  # should be True in production
    authjwt_denylist_token_checks: set = {"access"}


config = Config()


jwt_config = JWTConfig()
