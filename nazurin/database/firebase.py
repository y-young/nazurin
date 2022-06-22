import json

import firebase_admin
from firebase_admin import credentials, firestore

from nazurin.config import env
from nazurin.utils.decorators import async_wrap

class Firebase:
    """Firestore driver of Firebase."""
    def __init__(self):
        """Load credentials and initialize Firebase app."""
        cert = env.str('GOOGLE_APPLICATION_CREDENTIALS')
        if cert.startswith('{'):
            cert = json.loads(cert)
        cred = credentials.Certificate(cert)
        if len(firebase_admin._apps) == 0:
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self._collection = None
        self._document = None

    def collection(self, key):
        self._collection = self.db.collection(str(key))
        return self

    def document(self, key=None):
        self._document = self._collection.document(str(key))
        return self

    @async_wrap
    def get(self):
        return self._document.get().to_dict()

    @async_wrap
    def exists(self):
        return self._document.get().exists

    @async_wrap
    def insert(self, key, data):
        if key:
            return self._collection.document(str(key)).set(data)
        return self._collection.add(data)

    @async_wrap
    def update(self, data):
        return self._document.update(data)

    @async_wrap
    def delete(self):
        return self._document.delete()
