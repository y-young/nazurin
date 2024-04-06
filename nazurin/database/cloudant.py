from cloudant.client import Cloudant as CloudantBase
from requests.adapters import HTTPAdapter

from nazurin.config import RETRIES, env
from nazurin.database import DatabaseDriver
from nazurin.utils.decorators import async_wrap

with env.prefixed("CLOUDANT_"):
    USERNAME = env.str("USER")
    APIKEY = env.str("APIKEY")
    DATABASE = env.str("DB", default="nazurin")


class Cloudant(DatabaseDriver):
    """Cloudant driver of IBM Cloud."""

    def __init__(self):
        """Connect to database."""
        self.client = CloudantBase.iam(
            USERNAME,
            APIKEY,
            timeout=5,
            adapter=HTTPAdapter(max_retries=RETRIES),
        )
        self.client.connect()
        self.db = self.client[DATABASE]
        self._partition = None
        self._document = None

    def collection(self, key):
        self._partition = str(key)
        return self

    def document(self, key=None):
        self._document = str(key)
        return self

    @async_wrap
    def get(self):
        try:
            return self.db[self._id()]
        except KeyError:
            return None

    @async_wrap
    def exists(self):
        return self._id() in self.db

    @async_wrap
    def insert(self, key, data):
        self._document = str(key)
        data["_id"] = self._id()
        return self.db.create_document(data)

    @async_wrap
    def update(self, data):
        doc = self.db[self._id()]
        doc.update(data)
        return doc.save()

    @async_wrap
    def delete(self):
        doc = self.db[self._id()]
        return doc.delete()

    def _id(self):
        return ":".join((self._partition, self._document))

    def __del__(self):
        """Disconnect from database."""
        self.client.disconnect()
