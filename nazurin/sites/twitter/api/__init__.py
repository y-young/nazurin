from nazurin.models import Illust

from ..config import API, TwitterAPI
from .syndication import SyndicationAPI
from .web import WebAPI


class Twitter:
    syndication = SyndicationAPI()
    web = WebAPI()

    async def fetch(self, status_id: int) -> Illust:
        """Fetch & return tweet images and information."""
        if API == TwitterAPI.SYNDICATION:
            return await Twitter.syndication.fetch(status_id)
        if API == TwitterAPI.WEB:
            return await Twitter.web.fetch(status_id)


__all__ = ["Twitter"]
