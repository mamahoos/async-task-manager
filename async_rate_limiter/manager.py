import asyncio
from collections import deque
from typing import Optional

from .task import Task
from .strategies.base import RateLimitStrategy


class RateLimitedTaskManager:
    def __init__(self, strategy: RateLimitStrategy, worker_delay: float = 0.01):
        self.queue: deque[Task] = deque()
        self.strategy           = strategy
        self._running           = False
        self.delay: float       = worker_delay
        self._task: Optional[asyncio.Task] = None

    def add_task(self, coro) -> None:
        """Wraps and adds a coroutine to the queue."""
        self.queue.append(Task(coro))

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _worker(self) -> None:
        while self._running:
            if not self.queue:
                await asyncio.sleep(self.delay)
                continue

            await self.strategy.allow()

            task = self.queue.popleft()
            asyncio.create_task(task.run())