from __future__ import annotations
import asyncio
from typing import Any, Awaitable, Dict, Optional
from .task import Task
from .strategies.base import BaseStrategy


class TaskManager:
    def __init__(self, strategy: BaseStrategy, poll_interval: float = 0.01) -> None:
        self.strategy       = strategy
        self.poll_interval  = self._validate_poll_interval(poll_interval)
        self._running: bool = False

    async def add_task[T](self, coro: Awaitable[T], **metadata: Any) -> T:
        task = Task(coro, metadata)
        self.strategy.add_task(task)
        return await task.run()

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
    
    async def idle(self) -> None:
        asyncio.create_task(self.run())

    async def stop(self) -> None:
        self._running = False

    async def _execute_task(self, task: Task) -> None:
        await task.run()
        await self.strategy.on_task_done()

    @staticmethod
    def _validate_poll_interval(poll_interval: float, /) -> float:
        if poll_interval <= 0.0:
            raise ValueError(f"poll_interval must be greater than 0.0, got {poll_interval}")
        
        return poll_interval