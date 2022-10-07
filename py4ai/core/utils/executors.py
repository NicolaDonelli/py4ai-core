"""Module with helpers to be used in async programming."""

import asyncio
from typing import Any, Coroutine, Optional, TypeVar

T = TypeVar("T")


class AsyncExecutor:
    """Helper class for computing async execution as sync."""

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """Instantiate the helper class.

        :param loop: EventLoop to be used to resolving co-routines. If None, the running EventLoop will be taken.
        """
        self.loop = asyncio.get_event_loop() if loop is None else loop

    def execute(self, f: Coroutine[Any, Any, T]) -> T:
        """Execute co-routing synchronously.

        :param f: co-routine to be executed.
        :returns: output of the co-routine.
        """
        t = self.loop.create_task(f)
        return self.loop.run_until_complete(t)
