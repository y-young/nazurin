import os
import json
import firebase_admin
from firebase_admin import firestore, credentials

class Firebase(object):
    def __init__(self):
        cert = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if cert.startswith('{'):
            cert = json.loads(cert)
        cred = credentials.Certificate(cert)
        if len(firebase_admin._apps) == 0:
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def collection(self, key):
        self._collection = self.db.collection(str(key))
        return self

    def document(self, key=None):
        self._document = self._collection.document(str(key))
        return self

    def get(self):
        return self._document.get().to_dict()

    def exists(self):
        return self._document.get().exists

    def insert(self, key, data):
        if key:
            return self._collection.document(str(key)).set(data)
        else:
            return self._collection.add(data)

    def update(self, data):
        return self._document.update(data)