import firebase_admin
from firebase_admin import firestore

class Firebase(object):
    def __init__(self):
        firebase_admin.initialize_app()
        self.db = firestore.client()

    def get(self, collection, document):
        return self.db.collection(collection).document(str(document)).get().to_dict()

    def exists(self, collection, document):
        return self.db.collection(collection).document(str(document)).get().exists

    def store(self, collection, document, data):
        return self.db.collection(collection).document(str(document)).set(data)

    def update(self, collection, document, data):
        return self.db.collection(collection).document(str(document)).set(data)