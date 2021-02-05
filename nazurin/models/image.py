from dataclasses import dataclass

from nazurin.utils import Request, logger

from .file import File

@dataclass
class Image(File):
    thumbnail: str = None
    _size: int = 0
    _chosen_url: str = None

    async def display_url(self) -> str:
        return await self.chosen_url()

    async def chosen_url(self) -> str:
        if self._chosen_url:
            return self._chosen_url
        self._chosen_url = self.url
        if self.thumbnail:
            size = await self.size()
            if size > 5 * 1024 * 1024:
                self._chosen_url = self.thumbnail
                logger.info('Use thumbnail: %s', self._chosen_url)
        return self._chosen_url

    async def size(self) -> int:
        if self._size:
            return self._size
        async with Request(
                headers={'Referer': 'https://www.pixiv.net/'}) as request:
            async with request.head(self.url) as response:
                headers = response.headers

        if 'Content-Length' in headers.keys():
            self._size = int(headers['Content-Length'])
        return self._size

    def set_size(self, value: int):
        self._size = value
