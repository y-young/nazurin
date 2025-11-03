"""Nazurin database drivers and database manager."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from nazurin.config import DATABASE

if TYPE_CHECKING:
    from collections.abc import Callable


class Database:
    """Nazurin database manager."""

    def __init__(self):
        """Dynamically load all database drivers."""
        module = importlib.import_module("nazurin.database." + DATABASE.lower())
        self.driver: Callable[..., DatabaseDriver] = getattr(module, DATABASE)


class DatabaseDriver:
    def collection(self, key: str) -> DatabaseDriver:
        raise NotImplementedError

    def document(self, key: str | int) -> DatabaseDriver:
        raise NotImplementedError

    async def get(self) -> dict | None:
        raise NotImplementedError

    async def exists(self) -> bool:
        raise NotImplementedError

    async def insert(self, key: str | int | None, data: dict) -> bool:
        raise NotImplementedError

    async def update(self, data: dict) -> bool:
        raise NotImplementedError

    async def delete(self) -> bool:
        raise NotImplementedError
