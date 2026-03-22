from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError
from typing_extensions import Self

if TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection
    from pymongo.asynchronous.database import AsyncDatabase

from nazurin.config import env
from nazurin.database import DatabaseDriver
from nazurin.utils.exceptions import NazurinError


class Mongo(DatabaseDriver):
    """MongoDB driver for MongoDB Atlas or local server."""

    def __init__(self):
        """Load credentials and initialize client."""
        self.db = self.get_database()
        self._collection: AsyncCollection | None = None
        self._document: str | int | None = None

    @classmethod
    @lru_cache
    def get_database(cls) -> AsyncDatabase:
        uri = env.str("MONGO_URI", default="mongodb://localhost:27017/nazurin")
        client = AsyncMongoClient(uri)
        return client.get_default_database()

    def collection(self, key: str) -> Self:
        self._collection = self.db[key]
        return self

    def document(self, key: str | int) -> Self:
        self._document = key
        return self

    async def get(self) -> dict | None:
        assert self._collection is not None
        return await self._collection.find_one({"_id": self._document})

    async def exists(self) -> bool:
        assert self._collection is not None
        count = await self._collection.count_documents({"_id": self._document}, limit=1)
        return count > 0

    async def insert(self, key: str | int | None, data: dict) -> bool:
        if key:
            data["_id"] = key
        assert self._collection is not None
        try:
            result = await self._collection.insert_one(data)
            return result.acknowledged
        except DuplicateKeyError as error:
            raise NazurinError("Already exists in database.") from error

    async def update(self, data: dict) -> bool:
        assert self._collection is not None
        result = await self._collection.update_one(
            {"_id": self._document},
            {"$set": data},
        )
        return result.modified_count == 1

    async def delete(self) -> bool:
        assert self._collection is not None
        result = await self._collection.delete_one({"_id": self._document})
        return result.deleted_count == 1
