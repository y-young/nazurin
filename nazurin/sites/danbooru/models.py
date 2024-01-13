from dataclasses import dataclass

from nazurin.models import Illust
from nazurin.utils.network import CloudScraperRequest


@dataclass
class DanbooruIllust(Illust):
    async def download(self, **kwargs):
        await super().download(request_class=CloudScraperRequest, **kwargs)
