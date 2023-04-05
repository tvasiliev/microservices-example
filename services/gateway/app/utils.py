from typing import cast

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password) -> str:
    """Turns given password into hash-string"""
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password, hashed_password) -> bool:
    """Compares given password to hash-string"""
    return cast(bool, pwd_context.verify(plain_password, hashed_password))
