from __future__ import annotations
import abc
from typing import Optional
from ..task import Task


class BaseStrategy(abc.ABC):
    @abc.abstractmethod
    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_next_task(self) -> Optional[Task]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_sleep_interval(self) -> Optional[float]:
        raise NotImplementedError

    async def on_task_done(self) -> None:
        """
        Called after a task finishes.
        Default implementation does nothing.
        Strategies that need to update internal state override this.
        """
        pass
