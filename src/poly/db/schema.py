from pydantic import BaseModel, field_validator

Permission = dict[str, str | list[str]]


class Base(BaseModel):
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str


class Resource(BaseModel):
    name: str


class Resources(BaseModel):
    resources: list[Resource]


class Role(Base):
    name: str


class Branch(Base):
    address: str
    city: str
    name: str
    state: str
    township: str


class NewBranch(BaseModel):
    name: str
    address: str
    township_id: int

    @field_validator("name")
    @classmethod
    def name_cannot_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty.")
        return v

    @field_validator("address")
    @classmethod
    def address_cannot_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Address cannot be empty.")
        return v


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
