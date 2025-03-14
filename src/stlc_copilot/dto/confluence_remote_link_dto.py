from pydantic import BaseModel, HttpUrl, RootModel

class Object(BaseModel):
    url: str
    
class RemoteLink(BaseModel):
    id: int
    self: HttpUrl
    object: Object

class RemoteLinkList(RootModel):
    root: list[RemoteLink]