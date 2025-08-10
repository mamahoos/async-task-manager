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
        self.delay_seconds = self._validate_delay_seconds(delay_seconds)
        self._last_run     = 0
        self._lock         = asyncio.Lock()
        self.tasks: deque[Task] = deque()
        
    @staticmethod
    def _validate_delay_seconds(delay_seconds: float, /) -> float:
        """
        Validates the delay_seconds parameter.
        
        Args:
            delay_seconds: Fixed delay between executions.
            
        Returns:
            float: Validated delay_seconds value
            
        Raises:
            TypeError: If delay_seconds is not a float
            ValueError: If delay_seconds is less than or equal to 0.0
        """
        if not isinstance(delay_seconds, float):
            raise TypeError(f"delay_seconds must be a float, got {type(delay_seconds).__name__}")
        
        if delay_seconds <= 0.0:
            raise ValueError(f"delay_seconds must be greater than 0.0, got {delay_seconds}")
        
        return delay_seconds

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
