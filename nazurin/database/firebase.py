import json
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore_async
from google.cloud.firestore import AsyncClient

from nazurin.config import env
from nazurin.database import DatabaseDriver


class Firebase(DatabaseDriver):
    """Firestore driver of Firebase."""

    db: AsyncClient

    def __init__(self):
        """Load credentials and initialize Firebase app."""
        cert = env.str("GOOGLE_APPLICATION_CREDENTIALS")
        if cert.startswith("{"):
            cert = json.loads(cert)
        cred = credentials.Certificate(cert)
        if len(firebase_admin._apps) == 0:
            firebase_admin.initialize_app(cred)
        self.db = firestore_async.client()
        self._collection = None
        self._document = None

    def collection(self, key):
        self._collection = self.db.collection(str(key))
        return self

    def document(self, key=None):
        self._document = self._collection.document(str(key))
        return self

    async def list(self, page_size: Optional[int] = None):
        return self._collection.list_documents(page_size)

    async def get(self):
        document = await self._document.get()
        return document.to_dict()

    async def exists(self) -> bool:
        document = await self._document.get()
        return document.exists

    async def insert(self, key, data):
        if key:
            return await self._collection.document(str(key)).set(data)
        return await self._collection.add(data)

    async def update(self, data):
        return await self._document.update(data)

    async def delete(self):
        return await self._document.delete()
