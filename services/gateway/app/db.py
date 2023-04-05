from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import as_declarative, declared_attr, sessionmaker

from .config import config


@as_declarative()
class Base:
    """Base model with definitions of necessary methods and attributes"""

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
    metadata = sa.MetaData()

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return cls.__name__.lower()  # pylint: disable=no-member

    def to_dict(self):
        return vars(self)


class Role(Base):
    """Description for roles of users"""

    name = sa.Column(sa.String, nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class User(Base):
    """Description for users of application"""

    # outer_id = sa.Column(sa.String, unique=True)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    username = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False, unique=True)
    password_hash = sa.Column(sa.String, nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey("role.id"), nullable=False)

    def __init__(
        self, first_name, last_name, username, email, password_hash, role_id
    ) -> None:
        # self.outer_id = outer_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role_id = role_id


engine = sa.create_engine(config.POSTGRES_URL, echo=True)


Session = sessionmaker(bind=engine)


def create_roles() -> None:
    """Fills user roles in corresponding table"""
    s = Session()
    s.add(Role(name="User"))
    s.add(Role(name="Manager"))
    s.add(Role(name="Administrator"))
    s.commit()


def drop_and_create() -> None:
    """Hard reset of database"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    create_roles()


def recreate_db() -> None:
    """Creation of database objects if they're absent"""
    if not sa.inspect(engine).has_table("role"):
        Role.__table__.create(bind=engine)
        create_roles()

    if not sa.inspect(engine).has_table("user"):
        User.__table__.create(bind=engine)


@sa.event.listens_for(User, "before_insert")
def modify_username(mapper, connect, target) -> None:
    """
    Name modification for new users. Allows to create multiple
    users with same username diversed only by additional number.
    Example: JohnJohnson#0234, JohnJohnson#2353
    """
    target.username += f"#{Session().query(User).count()+1:04d}"
