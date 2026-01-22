from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class DocumentCreate(BaseModel):
    content: str

class DocumentUpdate(BaseModel):
    content: str

class DocumentOut(BaseModel):
    id: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentListOut(BaseModel):
    items: List[DocumentOut]
    total: int
    page: int
    page_size: int        
