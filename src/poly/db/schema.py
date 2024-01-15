from pydantic import BaseModel

Permission = dict[str, str | list[str]]


class Base(BaseModel):
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str


class Resource(Base):
    name: str


class Resources(BaseModel):
    resources: list[Resource]
    total: int


class Role(Base):
    name: str


class Roles(BaseModel):
    roles: list[Role]
    total: int


class Token(BaseModel):
    access_token: str
    expires_in: int
    name: str
    permissions: list[Permission]
    role: str
    token_type: str
