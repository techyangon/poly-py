"""create states table

Revision ID: 2ea9aebb3255
Revises: 140d13359ed5
Create Date: 2024-01-16 16:40:37.133725

"""
import sqlalchemy as sa
from alembic import context, op

from poly.config import get_settings
from poly.db import UTCNow

# revision identifiers, used by Alembic.
revision = "2ea9aebb3255"
down_revision = "140d13359ed5"
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
        "states",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(settings.name_length), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime, server_default=UTCNow()),
        sa.Column("created_by", sa.String, nullable=False, default="system"),
        sa.Column(
            "updated_at", sa.DateTime, server_default=UTCNow(), onupdate=UTCNow()
        ),
        sa.Column("updated_by", sa.String, nullable=False, default="system"),
    )


def schema_downgrades() -> None:
    op.drop_table("states")


def data_upgrades() -> None:
    pass


def data_downgrades() -> None:
    op.execute("DELETE FROM states;")
    op.execute("ALTER SEQUENCE states_id_seq RESTART;")
