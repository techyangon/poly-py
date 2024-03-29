"""create branches table

Revision ID: 9ef70bfbd9e0
Revises: 1516dea1ae67
Create Date: 2024-01-16 20:16:11.958979

"""

import sqlalchemy as sa
from alembic import context, op

from poly.config import get_settings
from poly.db import UTCNow

# revision identifiers, used by Alembic.
revision = "9ef70bfbd9e0"
down_revision = "1516dea1ae67"
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
        "branches",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(settings.name_length), nullable=False, unique=True),
        sa.Column("address", sa.String(settings.address_length), nullable=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("township_id", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=UTCNow()),
        sa.Column("created_by", sa.String(settings.name_length), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime, server_default=UTCNow(), onupdate=UTCNow()
        ),
        sa.Column("updated_by", sa.String(settings.name_length), nullable=False),
        sa.ForeignKeyConstraint(
            ["township_id"], ["townships.id"], "fk_branches_township_id_townships"
        ),
    )


def schema_downgrades() -> None:
    op.drop_constraint("fk_branches_township_id_townships", "branches")
    op.drop_table("branches")


def data_upgrades() -> None:
    pass


def data_downgrades() -> None:
    op.execute("DELETE FROM branches;")
    op.execute("ALTER SEQUENCE branches_id_seq RESTART;")
