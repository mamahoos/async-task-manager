from abc import ABC, abstractmethod

class RateLimitStrategy(ABC):
    @abstractmethod
    async def allow(self) -> None:
        """Wait until the task is allowed to run."""
        pass
