import asyncio
import logging
from functools import partial, wraps

import tenacity
from aiogram.types import ChatActions, Message
from aiogram.utils.exceptions import RetryAfter

from nazurin import config

retry = tenacity.retry(stop=tenacity.stop_after_attempt(config.RETRIES),
                       before=tenacity.before_log(
                           logging.getLogger('tenacity'), logging.INFO))

def chat_action(action: str):
    """Sends `action` while processing."""
    def decorator(func):
        @wraps(func)
        async def wrapped_func(message: Message, *args, **kwargs):
            await asyncio.create_task(ChatActions._do(action))
            result = await asyncio.create_task(func(message, *args, **kwargs))
            return result

        return wrapped_func

    return decorator

def async_wrap(func):
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
            except RetryAfter as error:
                logging.getLogger('nazurin').warning(
                    'Hit flood limit, retry after %d seconds',
                    error.timeout + 1)
                await asyncio.sleep(error.timeout + 1)

    return decorator
