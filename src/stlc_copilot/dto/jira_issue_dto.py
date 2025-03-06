from typing import List, Optional
from pydantic import BaseModel
import json

class InnerContent(BaseModel):
    type: str
    text: str

class Content(BaseModel):
    type: str
    content: List[InnerContent]

class Project(BaseModel):
    id: str
    key: str

class Parent(BaseModel):
    id: str

class IssueType(BaseModel):
    id: str
    name: str

class Fields(BaseModel):
    project: Project
    summary: str
    description: str
    issuetype: IssueType
    parent: Optional[Parent] = None  # Parent is now optional

class Issue(BaseModel):
    id: str
    key: str
    fields: Fields
    

    def toJson(self):
        return self.json()

class JiraIssueBulk(BaseModel):
    issueUpdates: List[Issue]
