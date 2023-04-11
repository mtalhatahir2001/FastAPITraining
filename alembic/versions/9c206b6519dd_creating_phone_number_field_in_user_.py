"""creating phone number field in user table

Revision ID: 9c206b6519dd
Revises: 
Create Date: 2023-04-01 14:54:03.248894

"""
import logging

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9c206b6519dd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    logging.info(f"Adding new column .. from {__name__}")
    op.add_column("Users", sa.Column("p_number", sa.String(11), nullable=True))


def downgrade() -> None:
    logging.info(f"Dropping new column .. from {__name__}")
    op.drop_column("Users", "p_number")
