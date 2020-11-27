import requests
from dataclasses import dataclass
from config import DOWNLOAD_DIR
from utils import logger, sanitizeFilename

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
    def path(self):
        return DOWNLOAD_DIR + self.name

    @property
    def display_url(self):
        return self.chosen_url

    @property
    def chosen_url(self):
        if self._chosen_url:
            return self._chosen_url
        self._chosen_url = self.url
        if self.size > 5*1024*1024 and self.thumbnail:
            self._chosen_url = self.thumbnail
            logger.info('Use thumbnail: ' + self._chosen_url)
        return self._chosen_url

    @property
    def size(self):
        if self._size:
            return self._size
        headers = requests.head(self.url, headers={'Referer': 'https://www.pixiv.net/'}).headers
        if 'Content-Length' in headers.keys():
            self._size = int(headers['Content-Length'])
        return self._size

    @size.setter
    def size(self, value):
        self._size = value