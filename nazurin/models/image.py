from dataclasses import dataclass

from nazurin.utils import Request, logger
from nazurin.utils.exceptions import NazurinError

from .file import File

@dataclass
class Image(File):
    thumbnail: str = None
    _size: int = None
    width: int = 0
    height: int = 0
    _chosen_url: str = None

    async def display_url(self) -> str:
        return await self.chosen_url()

    async def chosen_url(self) -> str:
        # Conform with limitations of sending photos: https://core.telegram.org/bots/api#sendphoto
        if self._chosen_url:
            return self._chosen_url
        if self.height != 0 and self.width / self.height > 20:
            raise NazurinError(
                'Width and height ratio of image exceeds 20, try download option.'
            )
        self._chosen_url = self.url
        if self.thumbnail:
            # For safety reasons, use thumbnail when image size is unkown
            if (not self.width) or (
                    not self.height) or self.width + self.height > 10000:
                self._chosen_url = self.thumbnail
                logger.info(
                    'Use thumbnail (Unkown image size or width + height > 10000 [%s, %s]): %s',
                    self.width, self.height, self._chosen_url)
            else:
                size = await self.size()
                if (not size) or size > 5 * 1024 * 1024:
                    self._chosen_url = self.thumbnail
                    logger.info(
                        'Use thumbnail (Unknown size or size > 5MB [%s]): %s',
                        size, self._chosen_url)
        return self._chosen_url

    async def size(self) -> int:
        self._size = self._size or await super().size()
        if self._size:
            return self._size
        async with Request(
                headers={'Referer': 'https://www.pixiv.net/'}) as request:
            async with request.head(self.url) as response:
                headers = response.headers

        if 'Content-Length' in headers.keys():
            self._size = int(headers['Content-Length'])
            logger.info('Got image size: %s', self._size)
        else:
            logger.info('Failed to get image size')
        return self._size

    def set_size(self, value: int):
        self._size = value
