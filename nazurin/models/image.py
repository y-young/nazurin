import os
from dataclasses import dataclass

import requests

from nazurin.config import TEMP_DIR
from nazurin.utils import logger, sanitizeFilename

@dataclass
class Image:
    name: str
    url: str = None
    thumbnail: str = None
    _size: int = 0
    _chosen_url: str = None

    def __post_init__(self):
        self.name = sanitizeFilename(self.name)

    @property
    def path(self) -> str:
        return os.path.join(TEMP_DIR, self.name)

    @property
    def display_url(self) -> str:
        return self.chosen_url

    @property
    def chosen_url(self) -> str:
        if self._chosen_url:
            return self._chosen_url
        self._chosen_url = self.url
        if self.size > 5 * 1024 * 1024 and self.thumbnail:
            self._chosen_url = self.thumbnail
            logger.info('Use thumbnail: ' + self._chosen_url)
        return self._chosen_url

    @property
    def size(self) -> int:
        if self._size:
            return self._size
        headers = requests.head(self.url,
                                headers={
                                    'Referer': 'https://www.pixiv.net/'
                                }).headers
        if 'Content-Length' in headers.keys():
            self._size = int(headers['Content-Length'])
        return self._size

    @size.setter
    def size(self, value: int):
        self._size = value
