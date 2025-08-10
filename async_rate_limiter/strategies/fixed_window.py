from __future__ import annotations
import time
from collections import deque
from typing import Optional
from ..task import Task
from .base import BaseStrategy


class FixedWindowStrategy(BaseStrategy):
    """
    Allows only `max_requests` tasks in each `window_seconds` interval.
    Excess tasks wait until the next interval.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests   = max_requests
        self.window_seconds = window_seconds
        self.tasks          = deque()
        self.request_times  = deque()

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_next_task(self) -> Optional[Task]:
        now = time.time()
        # Remove old requests
        while self.request_times and now - self.request_times[0] >= self.window_seconds:
            self.request_times.popleft()

        if len(self.request_times) < self.max_requests and self.tasks:
            self.request_times.append(now)
            return self.tasks.popleft()
        return None

    async def get_sleep_interval(self) -> Optional[float]:
        if len(self.request_times) >= self.max_requests:
            # Time until next slot is available
            return self.window_seconds - (time.time() - self.request_times[0])
        return 0  # Check immediately
