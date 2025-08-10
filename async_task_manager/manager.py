from __future__ import annotations
import asyncio
from typing import Any, Awaitable, Dict
from .task import Task
from .strategies.base import BaseStrategy


class TaskManager:
    def __init__(self, strategy: BaseStrategy, poll_interval: float = 0.01) -> None:
        self.strategy      = strategy
        self.poll_interval = poll_interval
        self._running      = False
        self._worker_task  = None

    def add_task(self, coro: Awaitable[Any], metadata: Dict[str, Any] | None = None) -> None:
        task = Task(coro, metadata)
        self.strategy.add_task(task)

    async def run(self) -> None:
        self._running = True
        while self._running:
            task = self.strategy.get_next_task()
            if task:
                asyncio.create_task(self._execute_task(task))
            interval = await self.strategy.get_sleep_interval()
            if interval is None:
                await asyncio.sleep(self.poll_interval)
            else:
                await asyncio.sleep(interval)

    async def stop(self) -> None:
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()

    async def _execute_task(self, task: Task) -> None:
        await task.run()
        await self.strategy.on_task_done()

