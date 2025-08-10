from typing import Awaitable

class Task:
    def __init__(self, coro: Awaitable):
        self.coro = coro

    async def run(self):
        try:
            await self.coro
        except Exception as e:
            print(f"[Task] Error: {e}")
