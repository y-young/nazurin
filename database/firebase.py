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

    def get(self, collection, document):
        return self.db.collection(collection).document(str(document)).get().to_dict()

    def exists(self, collection, document):
        return self.db.collection(collection).document(str(document)).get().exists

    def store(self, collection, document, data):
        return self.db.collection(collection).document(str(document)).set(data)

    def update(self, collection, document, data):
        return self.db.collection(collection).document(str(document)).update(data)