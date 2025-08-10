import asyncio
import time
from collections import deque
from .base import RateLimitStrategy

class TokenBucketStrategy(RateLimitStrategy):
    def __init__(self, rate: int = 30, interval: float = 1.0):
        self.rate       = rate
        self.interval   = interval
        self.timestamps = deque()
        self.lock       = asyncio.Lock()

    async def allow(self) -> None:
        async with self.lock:
            now = time.monotonic()

            while self.timestamps and now - self.timestamps[0] > self.interval:
                self.timestamps.popleft()

            if len(self.timestamps) >= self.rate:
                sleep_time = self.interval - (now - self.timestamps[0])
                await asyncio.sleep(sleep_time)

            self.timestamps.append(time.monotonic())