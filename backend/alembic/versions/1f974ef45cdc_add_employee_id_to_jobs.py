"""add employer_id to jobs

Revision ID: 1f974ef45cdc
Revises: 2d9a25777f24
Create Date: 2026-08-17 12:26:37.959889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f974ef45cdc'
down_revision: Union[str, Sequence[str], None] = '2d9a25777f24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "jobs",
        sa.Column("employer_id", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("jobs", "employer_id")