"""Nazurin database drivers and database manager."""

from __future__ import annotations

import importlib
from ctypes import Union
from typing import Callable, Optional

from nazurin.config import DATABASE


class Database:
    """Nazurin database manager."""

    def __init__(self):
        """Dynamically load all database drivers."""
        module = importlib.import_module("nazurin.database." + DATABASE.lower())
        self.driver: Callable[..., DatabaseDriver] = getattr(module, DATABASE)


class DatabaseDriver:
    def collection(self, key: str) -> DatabaseDriver:
        raise NotImplementedError

    def document(self, key: Union[str, int]) -> DatabaseDriver:
        raise NotImplementedError

    async def get(self) -> Optional[dict]:
        raise NotImplementedError

    async def exists(self) -> bool:
        raise NotImplementedError

    async def insert(self, key: Optional[Union[str, int]], data: dict) -> bool:
        raise NotImplementedError

    async def update(self, data: dict) -> bool:
        raise NotImplementedError

    async def delete(self) -> bool:
        raise NotImplementedError
