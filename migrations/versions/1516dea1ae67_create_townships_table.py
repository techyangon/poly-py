"""create townships table

Revision ID: 1516dea1ae67
Revises: 5f9abd1a5252
Create Date: 2024-01-16 18:33:37.616161

"""
import sqlalchemy as sa
from alembic import context, op

from poly.config import get_settings
from poly.db import UTCNow

# revision identifiers, used by Alembic.
revision = "1516dea1ae67"
down_revision = "5f9abd1a5252"
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
        "townships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(settings.name_length), nullable=False),
        sa.Column("city_id", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=UTCNow()),
        sa.Column("created_by", sa.String, nullable=False, default="system"),
        sa.Column(
            "updated_at", sa.DateTime, server_default=UTCNow(), onupdate=UTCNow()
        ),
        sa.Column("updated_by", sa.String, nullable=False, default="system"),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], "fk_townships_city_id_cities"),
    )


def schema_downgrades() -> None:
    op.drop_constraint("fk_townships_city_id_cities", "townships")
    op.drop_table("townships")


def data_upgrades() -> None:
    pass


def data_downgrades() -> None:
    op.execute("DELETE FROM townships;")
    op.execute("ALTER SEQUENCE townships_id_seq RESTART;")
