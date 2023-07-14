"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import context, op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    schema_upgrades()
    if context.get_x_argument(as_dictionary=True).get("data", None):
      data_upgrades()


def downgrade() -> None:
    if context.get_x_argument(as_dictionary=True).get("data", None):
      data_downgrades()
    schema_downgrades()


def schema_upgrades() -> None:
    ${upgrades if upgrades else "pass"}


def schema_downgrades() -> None:
    ${downgrades if downgrades else "pass"}


def data_upgrades() -> None:
    pass


def data_downgrades() -> None:
    pass
