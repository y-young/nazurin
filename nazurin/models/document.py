from typing import Union

from pydantic import BaseModel


class Document(BaseModel):
    id: Union[int, str]
    collection: str
    data: dict
