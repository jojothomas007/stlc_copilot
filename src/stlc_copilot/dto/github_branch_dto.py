from typing import List, Optional
from pydantic import BaseModel


class Commit(BaseModel):
    sha: str

class Branch(BaseModel):
    name: str
    commit: Commit