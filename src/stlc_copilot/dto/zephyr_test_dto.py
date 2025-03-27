from typing import Optional, List, Union
from pydantic import BaseModel

class TestCase(BaseModel):
    id: int
    key: str
    name: str
    objective: Optional[str] = None
    precondition: Optional[str] = None
    