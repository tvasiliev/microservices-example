from pydantic import BaseModel


class UserJSON(BaseModel):
    """Sign in user credentials"""

    email: str
    password: str


class UserSignUpJSON(BaseModel):
    """Sign up user credentials"""

    username: str
    email: str
    password: str
    first_name: str
    last_name: str
