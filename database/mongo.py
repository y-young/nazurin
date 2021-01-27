from os import environ

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from utils import NazurinError

class Mongo(object):
    """MongoDB driver for MongoDB Atlas or local server."""
    def __init__(self):
        """Load credentials and initialize client."""
        URI = environ.get('MONGO_URI', 'mongodb://localhost:27017/nazurin')
        self.client = MongoClient(URI)
        self.db = self.client.get_default_database()

    def collection(self, key):
        self._collection = self.db[key]
        return self

    def document(self, key):
        self._document = key
        return self

    def get(self):
        return self._collection.find_one({'_id': self._document})

    def exists(self):
        return self._collection.count_documents({'_id': self._document},
                                                limit=1) > 0

    def insert(self, key, data):
        if key:
            data['_id'] = key
        try:
            return self._collection.insert_one(data).acknowledged
        except DuplicateKeyError:
            raise NazurinError('Already exists in database.')

    def update(self, data):
        return self._collection.update_one({
            '_id': self._document
        }, {
            '$set': data
        }).modified_count == 1

    def delete(self):
        return self._collection.delete_one({
            '_id': self._document
        }).deleted_count == 1
