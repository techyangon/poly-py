"""create roles table

Revision ID: e2e48de64931
Revises: 317f18663b6c
Create Date: 2023-07-16 14:02:40.562757

"""
import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.sql import column, table

from poly.db import UTCNow

# revision identifiers, used by Alembic.
revision = "e2e48de64931"
down_revision = "317f18663b6c"
branch_labels = None
depends_on = None


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
        "roles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=UTCNow()),
        sa.Column("created_by", sa.String, nullable=False),
        sa.Column(
            "updated_at", sa.DateTime, server_default=UTCNow(), onupdate=UTCNow()
        ),
        sa.Column("updated_by", sa.String, nullable=False),
    )


def schema_downgrades() -> None:
    op.drop_table("roles")


def data_upgrades() -> None:
    roles = table(
        "roles",
        column("name", sa.String),
        column("created_by", sa.String),
        column("updated_by", sa.String),
    )
    op.bulk_insert(
        roles,
        [
            {"name": "accountant", "created_by": "system", "updated_by": "system"},
            {"name": "admin", "created_by": "system", "updated_by": "system"},
            {"name": "lecturer", "created_by": "system", "updated_by": "system"},
            {"name": "receptionist", "created_by": "system", "updated_by": "system"},
            {"name": "staff", "created_by": "system", "updated_by": "system"},
        ],
    )


def data_downgrades() -> None:
    op.execute("DELETE FROM roles;")
    op.execute("ALTER SEQUENCE roles_id_seq RESTART;")
