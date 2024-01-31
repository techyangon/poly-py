import re
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
        v = v.strip()
        if not v:
            raise ValueError(f"{info.field_name} cannot be empty.")
        return v


class Branches(BaseModel):
    branches: list[Branch]
    total: int


class Token(BaseModel):
    access_token: str
    expires_in: int
    name: str
    token_type: str


class Permission(BaseModel):
    resource: str
    actions: list[str]


class Permissions(BaseModel):
    role: str
    permissions: list[Permission]


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


class Profile(BaseModel):
    created_at: str
    email: str
    id: int
    name: str
    role: str


class UserUpdate(BaseModel):
    id: int
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v) -> str:
        v = v.strip()
        if not re.match(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?\W)\S{8,}$", v):
            raise ValueError("Invalid password. Please check the rules again.")
        return v
