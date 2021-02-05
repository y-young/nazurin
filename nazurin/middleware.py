from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from nazurin import config

class AuthMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        if config.IS_PUBLIC:
            return
        if message.chat.id in config.ALLOW_ID + config.ALLOW_GROUP\
            or message.from_user.id in config.ALLOW_ID\
            or message.from_user.username in config.ALLOW_USERNAME:
            return
        raise CancelHandler()
