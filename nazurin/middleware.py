from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from nazurin import config
from nazurin.utils import logger


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ):
        if config.IS_PUBLIC:
            return await handler(event, data)
        message = event.message
        allowed_chats = config.ALLOW_ID + config.ALLOW_GROUP + [config.ADMIN_ID]
        if (
            message.chat.id in allowed_chats
            or message.from_user.id in [*config.ALLOW_ID, config.ADMIN_ID]
            or message.from_user.username in config.ALLOW_USERNAME
        ):
            return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ):
        logger.info(
            "Message {}: {}",
            event.message_id,
            event.text or event.caption,
        )
        return await handler(event, data)
