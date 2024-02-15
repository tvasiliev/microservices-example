import datetime
import uuid

import sqlalchemy as sa
from modules.db import Base, DBManager


class Task(Base):
    """Relation with dashboard tasks"""

    public_id = sa.Column(sa.UUID, unique=True, default=uuid.uuid4)
    header = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    bounty = sa.Column(sa.Numeric, default=0)
    author_public_id = sa.Column(sa.UUID, index=True, nullable=False)
    state = sa.Column(sa.Integer, sa.ForeignKey("state.id"), nullable=False)
    executor_public_id = sa.Column(sa.UUID, index=True)


class TaskHistory(Base):
    """History of tasks in dashboard"""

    task_id = sa.Column(sa.Integer, sa.ForeignKey("task.id"), nullable=False)
    state = sa.Column(sa.Integer, sa.ForeignKey("state.id"), nullable=False)
    modifier_public_uuid = sa.Column(sa.UUID)
    event_datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)


class TaskState(Base):
    """State of tasks in dashboard"""

    name = sa.Column(sa.String, nullable=False, unique=True)


STATES = (
    {'name': 'Created'},
    {'name': 'In work'},
    {'name': 'Finished'},
    {'name': 'Cancelled'}
)


class TasksDBCreator(DBManager):
    """Allows to:
    - create default objects in DB tasks on startup
    - create sessions
    """

    DEFAULT_DATA = {
        TaskState: STATES
    }
    RELATIONS = (Task, TaskHistory, TaskState)
