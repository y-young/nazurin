from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from nazurin import config
from nazurin.utils import logger


class AuthMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: Message, _data: dict):
        if config.IS_PUBLIC:
            return
        allowed_chats = config.ALLOW_ID + config.ALLOW_GROUP + [config.ADMIN_ID]
        if (
            message.chat.id in allowed_chats
            or message.from_user.id in config.ALLOW_ID + [config.ADMIN_ID]
            or message.from_user.username in config.ALLOW_USERNAME
        ):
            return
        raise CancelHandler


class LoggingMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, _data: dict):
        logger.info(
            "Message {}: {}",
            message.message_id,
            message.text or message.caption,
        )
