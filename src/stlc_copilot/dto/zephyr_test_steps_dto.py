from typing import List, Optional
from pydantic import BaseModel

class InlineItem(BaseModel):
    description: str
    testData: Optional[str] = None
    expectedResult: Optional[str] = None  # Optional, as not all items might have 'expectedResult'

class Item(BaseModel):
    inline: InlineItem

class TestStepsPayload(BaseModel):
    mode: str
    items: List[Item]

class TestStepsResponse(BaseModel):
    total: int
    isLast: bool
    values: List[Item]