from typing import List, Union

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from .helpers import get_urls_from_message

class URLFilter(BoundFilter):
    key = 'url'

    # pylint: disable=arguments-differ
    async def check(self, message: Message) -> Union[List[str], bool]:
        urls = get_urls_from_message(message)
        if urls:
            return {'urls': urls}
        return False
