from pydantic import BaseModel


class Document(BaseModel):
    id: int | str
    collection: str
    data: dict
