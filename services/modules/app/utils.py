import asyncio
from typing import Coroutine


BACKGROUND_TASKS = set()


def add_task_to_loop(coroutine: Coroutine) -> None:
    """Creates task and stores strong reference to it"""
    task = asyncio.create_task(coroutine)
    BACKGROUND_TASKS.add(task)
    task.add_done_callback(BACKGROUND_TASKS.discard)