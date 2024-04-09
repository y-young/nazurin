import asyncio
import functools
from functools import partial, wraps
from typing import Callable, ClassVar, List

import tenacity
from aiogram.exceptions import TelegramRetryAfter
from aiohttp import ClientError, ClientResponseError
from async_lru import alru_cache
from tenacity import retry_if_exception, stop_after_attempt, wait_exponential

from nazurin import config
from nazurin.utils import logger


def after_log(retry_state):
    # Set frame depth to get the real caller
    logger.opt(depth=3).info(
        "{} during {} execution, {} of {} attempted.",
        repr(retry_state.outcome.exception()),
        tenacity._utils.get_callback_name(retry_state.fn),
        retry_state.attempt_number,
        config.RETRIES,
    )


def exception_predicate(exception):
    """Predicate to check if we should retry when an exception occurs."""
    if not isinstance(exception, (ClientError, asyncio.exceptions.TimeoutError)):
        return False
    if isinstance(exception, ClientResponseError):
        return exception.status in [408, 429, 500, 502, 503, 504]
    return True


network_retry = tenacity.retry(
    reraise=True,
    stop=stop_after_attempt(config.RETRIES),
    after=after_log,
    retry=retry_if_exception(exception_predicate),
    wait=wait_exponential(multiplier=1, max=8),
)


def async_wrap(func):
    """Transform a synchronous function to an asynchronous one."""

    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


def retry_after(func):
    """Retry after hitting flood limit."""

    @wraps(func)
    async def decorator(*args, **kwargs):
        while True:
            try:
                result = await func(*args, **kwargs)
                return result
            except TelegramRetryAfter as error:
                logger.opt(depth=1).warning(
                    "Hit flood limit, retry after {} seconds",
                    error.retry_after + 1,
                )
                await asyncio.sleep(error.retry_after + 1)

    return decorator


class Cache:
    cached_functions: ClassVar[List[Callable]] = []

    @staticmethod
    def lru(*args, **kwargs):
        """Least-recently-used cache decorator."""

        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                func = alru_cache(*args, **kwargs)(func)
            else:
                func = functools.lru_cache(*args, **kwargs)(func)
            Cache.cached_functions.append(func)
            return func

        return decorator

    @staticmethod
    def clear():
        for func in Cache.cached_functions:
            func.cache_clear()
