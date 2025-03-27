from typing import Optional, List
from pydantic import BaseModel

class Folder(BaseModel):
    id: int
    parentId: Optional[int]
    name: str

class Folders(BaseModel):
    next: Optional[str]
    startAt: int
    maxResults: int
    total: int
    isLast: bool
    values: List[Folder]
