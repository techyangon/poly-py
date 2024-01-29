"""create users table

Revision ID: 140d13359ed5
Revises: e2e48de64931
Create Date: 2023-07-18 11:19:57.207666

"""

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.sql import column, table

from poly.config import get_settings
from poly.db import UTCNow
from poly.services.auth import password_context

# revision identifiers, used by Alembic.
revision = "140d13359ed5"
down_revision = "e2e48de64931"
branch_labels = None
depends_on = None

settings = get_settings()


def upgrade() -> None:
    schema_upgrades()
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_upgrades()


def downgrade() -> None:
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_downgrades()
    schema_downgrades()


def schema_upgrades() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(settings.name_length), nullable=False),
        sa.Column(
            "email", sa.String(settings.email_length), unique=True, nullable=False
        ),
        sa.Column("password", sa.String(settings.password_hash_length), nullable=False),
        sa.Column("is_active", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=UTCNow()),
        sa.Column("created_by", sa.String, nullable=False),
        sa.Column(
            "updated_at", sa.DateTime, server_default=UTCNow(), onupdate=UTCNow()
        ),
        sa.Column("updated_by", sa.String, nullable=False),
    )


def schema_downgrades() -> None:
    op.drop_table("users")


def data_upgrades() -> None:
    users = table(
        "users",
        column("name", sa.String),
        column("email", sa.String),
        column("password", sa.String),
        column("is_active", sa.Boolean),
        column("created_by", sa.String),
        column("updated_by", sa.String),
    )
    op.bulk_insert(
        users,
        [
            {
                "name": settings.admin_username,
                "email": settings.admin_mail,
                "password": password_context.hash(settings.admin_password),
                "is_active": True,
                "created_by": "system",
                "updated_by": "system",
            }
        ],
    )


def data_downgrades() -> None:
    op.execute("DELETE FROM users;")
    op.execute("ALTER SEQUENCE users_id_seq RESTART;")
