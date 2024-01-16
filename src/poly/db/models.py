from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, MetaData, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from poly.config import get_settings
from poly.db import UTCNow

settings = get_settings()
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


class State(Base):
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(settings.name_length))
    cities: Mapped[list["City"]] = relationship(
        back_populates="state", cascade="all, delete", passive_deletes=True
    )
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String, default="system")
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String, default="system")


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(settings.name_length))
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"))
    state: Mapped["State"] = relationship(back_populates="cities")
    townships: Mapped[list["Township"]] = relationship(
        back_populates="city", cascade="all, delete", passive_deletes=True
    )
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String, default="system")
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String, default="system")


class Township(Base):
    __tablename__ = "townships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(settings.name_length))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    city: Mapped["City"] = relationship(back_populates="townships")
    branches: Mapped[list["Branch"]] = relationship(
        back_populates="branch", cascade="all, delete", passive_deletes=True
    )
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String, default="system")
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String, default="system")


class Resource(Base):  # type: ignore
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(settings.name_length))
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String(settings.name_length))
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String(settings.name_length))


class Role(Base):  # type: ignore
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(settings.name_length))
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String(settings.name_length))
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String(settings.name_length))


class User(Base):  # type: ignore
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(settings.name_length))
    email: Mapped[str] = mapped_column(String(settings.email_length))
    password: Mapped[str] = mapped_column(String(settings.password_hash_length))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String(settings.name_length))
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String(settings.name_length))


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(settings.name_length))
    address: Mapped[str] = mapped_column(String(settings.address_length))
    township_id: Mapped[int] = mapped_column(ForeignKey("townships.id"))
    township: Mapped["Township"] = relationship(back_populates="branches")
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String(settings.name_length))
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String(settings.name_length))
