from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    ValidationInfo,
    field_validator,
)

from poly.config import get_settings

settings = get_settings()


class Resources(BaseModel):
    resources: list[str]


class Role(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Annotated[str, StringConstraints(max_length=settings.name_length)]


class Roles(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    roles: list[Role]
    total: int


class Branch(BaseModel):
    id: int
    name: str
    address: str
    township: str
    city: str
    state: str
    created_by: str
    updated_at: str


class NewBranch(BaseModel):
    name: str
    address: str
    township_id: int

    @field_validator("name", "address")
    @classmethod
    def name_cannot_be_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty.")
        return v


class Branches(BaseModel):
    branches: list[Branch]
    total: int


class Permission(BaseModel):
    resource: str
    actions: list[str]


class Token(BaseModel):
    access_token: str
    expires_in: int
    name: str
    permissions: list[Permission]
    role: str
    token_type: str


class Township(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Annotated[str, StringConstraints(max_length=settings.name_length)]


class City(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Annotated[str, StringConstraints(max_length=settings.name_length)]
    townships: list[Township]


class State(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Annotated[str, StringConstraints(max_length=settings.name_length)]
    cities: list[City]


class Locations(BaseModel):
    states: list[State]
