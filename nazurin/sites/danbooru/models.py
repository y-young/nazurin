from dataclasses import dataclass

from nazurin.models import Illust
from nazurin.utils.network import CurlRequest


@dataclass
class DanbooruIllust(Illust):
    async def download(self, **kwargs):
        await super().download(request_class=CurlRequest, **kwargs)
