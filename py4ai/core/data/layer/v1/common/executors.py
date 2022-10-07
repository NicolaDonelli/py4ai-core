import asyncio
from typing import Any, Coroutine, Optional, TypeVar

T = TypeVar("T")


class AsyncExecutor:
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.loop = asyncio.get_event_loop() if loop is None else loop

    def __execute__(self, f: Coroutine[Any, Any, T]) -> T:
        t = self.loop.create_task(f)
        return self.loop.run_until_complete(t)
