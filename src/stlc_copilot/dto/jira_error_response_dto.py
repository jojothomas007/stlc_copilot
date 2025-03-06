from typing import List, Optional, Dict
from pydantic import BaseModel

class Errors(BaseModel):
    additionalProperties: Dict[str, str]

class JiraErrorResponse(BaseModel):
    errorMessages: List[str]
    errors: Errors
    status: Optional[int] = None  # status is optional
