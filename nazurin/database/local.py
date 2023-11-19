from os import path

from tinydb import Query, TinyDB

from nazurin.config import DATA_DIR
from nazurin.database import DatabaseDriver
from nazurin.utils.helpers import ensure_existence


class Local(DatabaseDriver):
    """Local database driver using TinyDB."""

    def __init__(self):
        ensure_existence(DATA_DIR)
        self.db = None
        self._key = None

    def collection(self, key):
        self.db = TinyDB(path.join(DATA_DIR, key + ".json"))
        return self

    def document(self, key):
        self._key = key
        return self

    async def get(self):
        document = Query()
        result = self.db.search(document.key == self._key)
        if result:
            return result[0]
        return None

    async def exists(self) -> bool:
        document = Query()
        return self.db.contains(document.key == self._key)

    async def insert(self, key, data):
        if key:
            data["key"] = key
        return self.db.insert(data)

    async def update(self, data):
        document = Query()
        return self.db.update(data, document.key == self._key)

    async def delete(self):
        document = Query()
        return self.db.remove(document.key == self._key)
