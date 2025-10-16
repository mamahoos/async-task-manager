from asyncio import Future
from typing  import Any, Awaitable, Dict


class Task[T](Future[T]):
    """
    Represents an asynchronous task that behaves like a Future.
    """

    __slots__ = ('coro', 'metadata')

    def __init__(self, coro: Awaitable[T], metadata: Dict[str, Any]) -> None:
        super().__init__()
        self.coro    : Awaitable[T]   = coro
        self.metadata: Dict[str, Any] = metadata

    async def run(self) -> T:
        """
        Executes the coroutine and sets the result on completion.
        """
        try:
            result = await self.coro
            if not self.done():
                self.set_result(result)
        except Exception as e:
            if not self.done():
                self.set_exception(e)
            raise
        return await self