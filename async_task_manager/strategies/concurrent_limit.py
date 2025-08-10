from __future__ import annotations
import asyncio
from collections import deque
from typing import Optional
from ..task import Task
from .base import BaseStrategy


class ConcurrentLimitStrategy(BaseStrategy):
    """
    Limits the number of concurrently running tasks.
    """

    def __init__(self, max_concurrent: int) -> None:
        self.max_concurrent = max_concurrent
        self.tasks          = deque()
        self.running        = 0
        self._lock          = asyncio.Lock()

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_next_task(self) -> Optional[Task]:
        if self.running < self.max_concurrent and self.tasks:
            self.running += 1
            return self.tasks.popleft()
        return None

    async def get_sleep_interval(self) -> Optional[float]:
        if self.running >= self.max_concurrent:
            return None  # Wait indefinitely
        return 0

    async def on_task_done(self) -> None:
        async with self._lock:
            self.running -= 1
