from typing import List, Union

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from .helpers import getUrlsFromMessage

class URLFilter(BoundFilter):
    key = 'url'

    async def check(self, message: Message) -> Union[List[str], bool]:
        urls = getUrlsFromMessage(message)
        if urls:
            return {'urls': urls}
        return False
