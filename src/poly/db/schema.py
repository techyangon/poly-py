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


class Branch(Base):
    address: str
    city: str
    name: str
    state: str
    township: str


class Roles(BaseModel):
    roles: list[Role]
    total: int


class Branches(BaseModel):
    branches: list[Branch]
    total: int


class Token(BaseModel):
    access_token: str
    expires_in: int
    name: str
    permissions: list[Permission]
    role: str
    token_type: str


class Location(BaseModel):
    name: str
    value: int


class Township(Location):
    pass


class City(Location):
    townships: list[Township]


class State(Location):
    cities: list[City]


class LocationResponse(BaseModel):
    states: list[State]
