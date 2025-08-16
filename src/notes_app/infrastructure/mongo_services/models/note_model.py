from typing import Optional
from bson import ObjectId
from beanie import Document
from pydantic import ConfigDict


class NoteMongo(Document):
    note_id: int
    content: str
    owner_id: int
    parent_id: Optional[ObjectId] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    class Settings:
        name = "notes"
