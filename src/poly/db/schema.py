from pydantic import BaseModel


class Resource(BaseModel):
    name: str
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str


class Resources(BaseModel):
    resources: list[Resource]
    total: int
