"""create cities table

Revision ID: 5f9abd1a5252
Revises: 2ea9aebb3255
Create Date: 2024-01-16 16:55:49.251557

"""

import sqlalchemy as sa
from alembic import context, op

from poly.config import get_settings
from poly.db import UTCNow

# revision identifiers, used by Alembic.
revision = "5f9abd1a5252"
down_revision = "2ea9aebb3255"
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
        "cities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(settings.name_length), nullable=False, unique=True),
        sa.Column("state_id", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=UTCNow()),
        sa.Column("created_by", sa.String, nullable=False, default="system"),
        sa.Column(
            "updated_at", sa.DateTime, server_default=UTCNow(), onupdate=UTCNow()
        ),
        sa.Column("updated_by", sa.String, nullable=False, default="system"),
        sa.ForeignKeyConstraint(
            ["state_id"], ["states.id"], "fk_cities_state_id_states"
        ),
    )


def schema_downgrades() -> None:
    op.drop_constraint("fk_cities_state_id_states", "cities")
    op.drop_table("cities")


def data_upgrades() -> None:
    pass


def data_downgrades() -> None:
    op.execute("DELETE FROM cities;")
    op.execute("ALTER SEQUENCE cities_id_seq RESTART;")
