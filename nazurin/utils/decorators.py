import asyncio
import logging
from functools import partial, wraps

import tenacity
from aiogram.types import ChatActions, Message
from aiogram.utils.exceptions import RetryAfter

from nazurin import config

def after_log(retry_state):
    logging.getLogger('tenacity').log(
        logging.INFO, '%s during %s execution, %s of %s attempted.',
        repr(retry_state.outcome.exception()),
        tenacity._utils.get_callback_name(retry_state.fn),
        retry_state.attempt_number, config.RETRIES)

retry = tenacity.retry(reraise=True,
                       stop=tenacity.stop_after_attempt(config.RETRIES),
                       after=after_log)

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
