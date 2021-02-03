from typing import Optional, Union

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from nazurin.config import env
from nazurin.utils.exceptions import NazurinError

class Mongo(object):
    """MongoDB driver for MongoDB Atlas or local server."""
    def __init__(self):
        """Load credentials and initialize client."""
        URI = env.str('MONGO_URI', default='mongodb://localhost:27017/nazurin')
        self.client = AsyncIOMotorClient(URI)
        self.db = self.client.get_default_database()

    def collection(self, key: str):
        self._collection = self.db[key]
        return self

    def document(self, key: Union[str, int]):
        self._document = key
        return self

    async def get(self) -> Optional[dict]:
        return await self._collection.find_one({'_id': self._document})

    async def exists(self) -> bool:
        count = await self._collection.count_documents({'_id': self._document},
                                                       limit=1)
        return count > 0

    async def insert(self, key: Optional[Union[str, int]], data: dict) -> bool:
        if key:
            data['_id'] = key
        try:
            result = await self._collection.insert_one(data)
            return result.acknowledged
        except DuplicateKeyError as error:
            raise NazurinError('Already exists in database.') from error

    async def update(self, data: dict) -> bool:
        result = await self._collection.update_one({'_id': self._document},
                                                   {'$set': data})
        return result.modified_count == 1

    async def delete(self) -> bool:
        result = await self._collection.delete_one({'_id': self._document})
        return result.deleted_count == 1
