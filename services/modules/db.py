import re

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy.dialects.postgresql import insert


@as_declarative()
class Base:
    """Base relation model with PK"""

    id = sa.Column(sa.Integer, primary_key=True)
    metadata = sa.MetaData()

    @declared_attr
    def __tablename__(cls) -> str:
        return '_'.join(re.findall('[A-Z][^A-Z]*', cls.__name__)).lower()

    def to_dict(self):
        return vars(self)

    def __init__(self, **kwargs) -> None:
        columns = [column.key for column in self.__table__.columns]

        for key, value in kwargs.items():
            if key not in columns:
                raise ValueError(f'Invalid column: {key}')
            setattr(self, key, value)


class DBManager:
    """Allows to:
    - create default objects in DB on startup
    - create sessions
    """

    DEFAULT_DATA: dict = {}
    RELATIONS: tuple = ()

    def __init__(self, postgres_url: str) -> None:
        self._engine = sa.create_engine(postgres_url, echo=True)
        self.session = sessionmaker(bind=self._engine)

    def _upsert_default_values(self) -> None:
        session = self.session()
        for relation, entries in self.DEFAULT_DATA.items():
            insert_expr = insert(relation).values(entries).on_conflict_do_nothing()
            session.execute(insert_expr)
        session.commit()

    def add_absent_data_to_db(self) -> None:
        """Creation of database objects if they're absent"""
        for relation in self.RELATIONS:
            if not sa.inspect(self._engine).has_table(relation.__tablename__):
                relation.__table__.create(bind=self._engine)

        self._upsert_default_values()


    def drop_and_create_db(self) -> None:
        """Hard reset of database"""
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        
        self._upsert_default_values()
