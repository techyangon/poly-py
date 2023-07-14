"""create resources table

Revision ID: 317f18663b6c
Revises:
Create Date: 2023-07-15 02:01:16.867824

"""
import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.sql import column, table

from poly.db import UTCNow

# revision identifiers, used by Alembic.
revision = "317f18663b6c"
down_revision = None
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
        "resources",
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
    op.drop_table("resources")


def data_upgrades() -> None:
    roles = table(
        "resources",
        column("name", sa.String),
        column("created_by", sa.String),
        column("updated_by", sa.String),
    )
    op.bulk_insert(
        roles,
        [
            {"name": "role", "created_by": "admin", "updated_by": "admin"},
            {"name": "staff", "created_by": "admin", "updated_by": "admin"},
        ],
    )


def data_downgrades() -> None:
    op.execute("DELETE FROM resources")
    op.execute("ALTER SEQUENCE resources_id_seq RESTART")
