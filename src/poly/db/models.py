from sqlalchemy import Boolean, DateTime, Integer, MetaData, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from poly.db import UTCNow

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String)
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String)
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    isActive: Mapped[bool] = mapped_column("is_active", Boolean, default=False)
    created_at = mapped_column(DateTime, server_default=UTCNow())
    created_by: Mapped[str] = mapped_column(String)
    updated_at = mapped_column(DateTime, server_default=UTCNow(), onupdate=UTCNow())
    updated_by: Mapped[str] = mapped_column(String)
