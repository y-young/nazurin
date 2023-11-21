from typing import Optional

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    username: str
    name: Optional[str]


class FileProperties(BaseModel):
    model_config = ConfigDict(extra="allow")

    width: int
    height: int


class File(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    type: str
    md5: str
    size: int
    properties: FileProperties
    url: Optional[str]
    thumbnailUrl: Optional[str]


class Note(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    createdAt: str
    userId: str
    user: User
    text: Optional[str]
    files: list[File]
    uri: Optional[str] = None
