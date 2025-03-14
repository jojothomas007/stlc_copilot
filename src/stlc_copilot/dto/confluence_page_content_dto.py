from pydantic import BaseModel

class BodyView(BaseModel):
    value: str

class Body(BaseModel):
    view: BodyView

class ConfluencePageContent(BaseModel):
    id: str
    type: str
    status: str
    title: str
    body: Body
