import uuid

import sqlalchemy as sa
from modules.db import Base, DBManager


class Role(Base):
    """Roles of users"""

    name = sa.Column(sa.String, nullable=False, unique=True)
    authority_level = sa.Column(sa.Integer, default=0)


class User(Base):
    """Users of application"""

    public_id = sa.Column(sa.UUID, unique=True, default=uuid.uuid4)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    username = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, index=True, nullable=False, unique=True)
    password_hash = sa.Column(sa.String, nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey("role.id"), nullable=False)
    is_active = sa.Column(sa.Boolean, index=True, default=True)


ROLES = (
    {"name": "User", "authority_level": 1},
    {"name": "Manager", "authority_level": 2},
    {"name": "Administrator", "authority_level": 3}
)


class GatewayDBManager(DBManager):
    """Allows to:
    - create default objects in DB gateway on startup
    - create sessions
    """

    DEFAULT_DATA = {
        Role: ROLES
    }
    RELATIONS = (Role, User)
