import datetime

import sqlalchemy as sa
from modules.db import Base, DBManager


class Wallet(Base):
    """User wallets"""

    user_public_id = sa.Column(sa.UUID, index=True, unique=True)
    balance = sa.Column(sa.Numeric, default=0)
    frozen_balance = sa.Column(sa.Numeric, default=0)


class Event(Base):
    """Description of actions that system may do with wallet"""

    name = sa.Column(sa.String, nullable=False, unique=True)


class Transaction(Base):
    """Actions made with wallet"""

    wallet_id = sa.Column(sa.Integer, sa.ForeignKey("wallet.id"), nullable=False)
    event_id = sa.Column(sa.Integer, sa.ForeignKey("event.id"), nullable=False)
    task_public_id = sa.Column(sa.UUID)
    margin = sa.Column(sa.Numeric, default=0)
    event_datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)


EVENTS = (
    {'name': 'Balance replenished'},
    {'name': 'Balance withdrawn'},
    {'name': 'Balance frozen'},
    {'name': 'Balance unfrozen'}
)


class BillingDBManager(DBManager):
    """Allows to:
    - create default objects in DB billing on startup
    - create sessions
    """

    DEFAULT_DATA = {
        Event: EVENTS
    }
    RELATIONS = (Wallet, Event, Transaction)
