from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    accountId: str
    emailAddress: str
    displayName: str