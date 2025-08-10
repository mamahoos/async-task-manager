from __future__ import annotations
import asyncio
from collections import deque
from typing import Optional
from ..task import Task
from .base import BaseStrategy


class DelayedStrategy(BaseStrategy):
    """
    Runs tasks with a fixed delay between executions.
    If a task is running, waits until it finishes before starting the next.
    """

    def __init__(self, delay_seconds: float) -> None:
        self.delay_seconds = delay_seconds
        self.tasks         = deque()
        self._last_run     = 0
        self._lock         = asyncio.Lock()

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_next_task(self) -> Optional[Task]:
        if not self.tasks:
            return None
        return self.tasks.popleft()

    async def get_sleep_interval(self) -> Optional[float]:
        if self._last_run > 0:
            elapsed = asyncio.get_event_loop().time() - self._last_run
            if elapsed < self.delay_seconds:
                return self.delay_seconds - elapsed
        return 0

    async def on_task_done(self) -> None:
        async with self._lock:
            self._last_run = asyncio.get_event_loop().time()
