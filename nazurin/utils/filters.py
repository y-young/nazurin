from typing import Dict, Union

from aiogram.filters.base import Filter
from aiogram.types import Message

from .helpers import get_urls_from_message


class URLFilter(Filter):
    async def __call__(self, message: Message) -> Union[bool, Dict]:
        urls = get_urls_from_message(message)
        if urls:
            return {"urls": urls}
        return False


class IDFilter(Filter):
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def __call__(self, message: Message) -> bool:
        return message.from_user and message.from_user.id == self.user_id
