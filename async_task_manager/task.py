from __future__ import annotations
import asyncio
from typing import Any, Awaitable, Dict, Optional


class Task:
    """
    Represents an asynchronous task with optional metadata.
    """
    
    __all__ = ('coro', 'metadata', '_result', '_done')

    def __init__(self, coro: Awaitable[Any], *metadata: Any) -> None:
        self.coro     = coro
        self.metadata = metadata
        self._result  = None
        self._done    = asyncio.Event()

    async def run(self) -> Any:
        """
        Executes the coroutine and stores the result.
        """
        try:
            self._result = await self.coro
        finally:
            self._done.set()
        return self._result

    async def wait(self) -> Any:
        """
        Waits for the task to finish and returns the result.
        """
        await self._done.wait()
        return self._result