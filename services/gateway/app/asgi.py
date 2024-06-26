import asyncio
import json

from fastapi import Depends, Request, Response
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse
from modules.app.app import create_app

from .config import jwt_config, config
from .db import User, GatewayDBManager
from .models import UserJSON, UserSignUpJSON
from .utils import hash_password, verify_password
from .rpc.server import GatewayRPCServer
from .rpc.client import GatewayRPCClient


app = create_app(rpc_server=GatewayRPCServer, rpc_client=GatewayRPCClient, config=config, database_manager=GatewayDBManager)


denied_tokens = set()


@AuthJWT.load_config
def get_config():
    """Configuration getter for fastapi-jwt-auth"""
    return jwt_config


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token) -> bool:
    jti = decrypted_token["jti"]
    return jti in denied_tokens


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_: Request, exc: AuthJWTException) -> JSONResponse:
    """Exceptions formatting"""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/sign-in")
async def sign_in(user: UserJSON, Authorize: AuthJWT = Depends()) -> JSONResponse:
    """Signs in user by given credentials"""
    Authorize.jwt_optional()

    current_user = Authorize.get_jwt_subject()
    if current_user is not None:
        return JSONResponse(
            {
                "message": "You have signed in already",
            },
            status_code=400,
        )

    user = user.dict()
    session = app.db_manager.session()
    user_entry = session.query(User).filter_by(email=user["email"]).first()
    if not user_entry or not verify_password(
        user["password"], user_entry.password_hash
    ):
        return JSONResponse(
            {
                "message": "Invalid email or password",
            },
            status_code=401,
        )

    response = JSONResponse({"message": "Authorized successfully"}, status_code=200)
    access_token = Authorize.create_access_token(subject=user["email"])
    Authorize.set_access_cookies(access_token, response=response)

    return response


@app.post("/sign-up", response_class=JSONResponse)
async def sign_up(user: UserSignUpJSON, Authorize: AuthJWT = Depends()) -> JSONResponse:
    """Signs up user by given credentials"""
    Authorize.jwt_optional()

    current_user = Authorize.get_jwt_subject()
    if current_user is not None:
        return JSONResponse(
            {
                "message": "Cannot create new user when signed in",
            },
            status_code=400,
        )

    user = user.dict()
    user["password_hash"] = hash_password(user["password"])
    del user["password"]

    s = app.db_manager.session()
    s.add(User(**user, role_id=1))
    try:
        s.commit()
    except IntegrityError:
        return JSONResponse(
            {
                "message": "User with such email already exists",
            },
            status_code=400,
        )

    return JSONResponse(
        {
            "message": "User has been created",
        },
        status_code=201,
    )


@app.post("/sign-out")
async def sign_out(Authorize: AuthJWT = Depends()) -> Response:
    """Signs out user if they are signed in"""
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()

    return Response(status_code=200)


@app.get("/")
async def main_page(request: Request, Authorize: AuthJWT = Depends()) -> Response:
    """Returns main page"""
    Authorize.jwt_optional()

    current_user = Authorize.get_jwt_subject()
    if current_user is not None:
        # TODO: return frame with 'signed in' header
        raise NotImplementedError

    # TODO: return frame with 'not signed in' header
    return app.templates.TemplateResponse("index.html", {"request": request, "user": None})


@app.get("/sign-in")
async def sign_in_page(request: Request, Authorize: AuthJWT = Depends()) -> Response:
    """
    Return sign-in form if user is not signed in
    Otherwise redirects to main page
    """
    Authorize.jwt_optional()

    current_user = Authorize.get_jwt_subject()
    if current_user is not None:
        # TODO: redirect to main page
        raise NotImplementedError

    # TODO: return frame with sign-in form
    raise NotImplementedError


@app.get("/sign-up")
async def sign_up_page(request: Request, Authorize: AuthJWT = Depends()) -> Response:
    """
    Return sign-up form if user is not signed in
    Otherwise redirects to main page
    """
    Authorize.jwt_optional()

    current_user = Authorize.get_jwt_subject()
    if current_user is not None:
        # TODO: redirect to main page
        raise NotImplementedError

    # TODO: return frame with sign-up form
    raise NotImplementedError


@app.get("/ping-tasks")
async def ping_task_service() -> Response:
    """Checks availability of tasks microservice"""
    response = await app.rabbitmq_client.request(
        routing_key='tasks.request',
        message_body={'text': 'ping from gateway'}
    )

    return JSONResponse(json.loads(response.decode()))


@app.get("/ping-billing")
async def ping_billing_service() -> Response:
    """Checks availability of billing microservice"""
    response = await app.rabbitmq_client.request(
        routing_key='billing.request',
        message_body={'text': 'ping from gateway'}
    )

    return JSONResponse(json.loads(response.decode()))
