import asyncio
import functools
import time
from asyncio import Task
from collections import defaultdict
from typing import DefaultDict, Any, Callable, ParamSpec, Tuple

import structlog
from starlette.concurrency import run_in_threadpool

from .settings import settings
from .utils import generate_transaction_id

logger = structlog.get_logger('_api_')

P = ParamSpec('P')


class CancelledTask(ValueError):
    pass


class NotExistingTask(ValueError):
    pass


class ResultNotSet(ValueError):
    pass


class BackgroundTask:
    def __init__(
            self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    async def __call__(self) -> None:
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(*self.args, **self.kwargs)
        else:
            return await run_in_threadpool(self.func, *self.args, **self.kwargs)


class BackgroundTasks:
    _tasks: DefaultDict[str, Tuple[Task, float]]
    _semaphore: asyncio.BoundedSemaphore | None

    def __init__(self, max_requests_at_time: int = 0) -> None:
        self._tasks = defaultdict()
        self._semaphore = asyncio.BoundedSemaphore(max_requests_at_time) if max_requests_at_time else None

    async def _executor(self, task: BackgroundTask):
        if not self._semaphore:
            return await task()
        else:
            async with self._semaphore:
                return await task()

    async def add_auto_named_task(
            self,
            func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs
    ) -> (str, Task):
        name = generate_transaction_id()
        return await self.add_task(name, func, *args, **kwargs)

    async def add_fire_and_forget_task(
            self,
            func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs
    ) -> Task:
        name = generate_transaction_id()
        task = await self.add_task(name, func, *args, **kwargs)
        task.add_done_callback(
            functools.partial(self._safe_remove_task_callback, name)
        )
        return task

    async def add_task(
            self,
            name: str,
            func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs,
    ) -> Task:
        background_task = BackgroundTask(func, *args, **kwargs)
        task = asyncio.create_task(
            self._executor(background_task),
            name=name
        )
        self._tasks[name] = task, time.time()  # UNIX time of start
        return task

    # noinspection PyUnusedLocal
    def _safe_remove_task_callback(self, name: str, task: Task = None):
        """
        Remove a task ensuring logging any exception throw
        """
        try:
            self.result_task(name, auto_remove=True)
        except Exception:  # noqa
            logger.exception(f'Error in background task: {name}')

    def remove_task(self, name: str, auto_cancel: bool = True):
        """
        Remove a task if exists
        """
        if name in self._tasks:
            task, start_time = self._tasks[name]
            if auto_cancel and not task.cancelled():
                task.cancel()
            del self._tasks[name]

    def result_task(self, name: str, auto_remove: bool = True):
        """
        If the task had any Exception, will be thrown from here
        """
        if name not in self._tasks:
            raise NotExistingTask

        task, start_time = self._tasks[name]

        could_auto_remove: bool = False
        try:
            if task.cancelled():
                could_auto_remove = True
                raise CancelledTask
            elif task.done():
                could_auto_remove = True
                result = task.result()
                return result
            else:
                raise ResultNotSet
        except Exception:
            # Raise any task Exception
            raise
        finally:
            if could_auto_remove and auto_remove:
                self.remove_task(name)

    def purge_tasks(self):
        """
        Purge all done or cancelled tasks that have been in memory for more than BACKGROUND_TASK_PERSISTENCE_LIMIT
        BE CAREFUL, can be deleted even if no-one called to result_task
        """
        for name in list(self._tasks.keys()):
            task, start_time = self._tasks[name]
            task_age = time.time() - start_time

            if (task.done() or task.cancelled()) and task_age > settings.BACKGROUND_TASK_PERSISTENCE_LIMIT:
                self._safe_remove_task_callback(name, None)

    async def garbage_collector(self):
        await asyncio.sleep(settings.BACKGROUND_TASK_GARBAGE_RESOLUTION)
        self.purge_tasks()
        await background_tasks.add_fire_and_forget_task(background_tasks.garbage_collector)


background_tasks = BackgroundTasks(settings.BACKGROUND_TASK_LIMIT)

_background_tasks = set()


def add_fire_and_forget_task(
        func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs
):
    task = asyncio.create_task(func(*args, **kwargs))

    # Add task to the set. This creates a strong reference.
    _background_tasks.add(task)

    # To prevent keeping references to finished tasks forever,
    # make each task remove its own reference from the set after
    # completion:
    task.add_done_callback(_background_tasks.discard)
