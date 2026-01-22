from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class TextCorpusCreate(BaseModel):
    content: str

class TextCorpusUpdate(BaseModel):
    content: str

class TextCorpusOut(BaseModel):
    id: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TextCorpusListOut(BaseModel):
    items: List[TextCorpusOut]
    total: int
    page: int
    page_size: int
