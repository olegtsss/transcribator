import asyncio
import functools
import logging
from typing import Any, Callable

from core.config import settings
from core.constants import Messanges
from fastapi import Response, status

logger = logging.getLogger(settings.app_title)


def controlled_timeout_task(timeout: int):
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            task = asyncio.create_task(func(*args, **kwargs))
            try:
                return await asyncio.wait_for(task, timeout=timeout)
            except asyncio.exceptions.TimeoutError:
                logger.warning(Messanges.TASK_CANCELED_FOR_TIMEOUT_COMMON.value, func.__name__)
                return Response(status_code=status.HTTP_408_REQUEST_TIMEOUT)
        return wrapped
    return wrapper
