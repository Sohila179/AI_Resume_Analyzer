"""add role to users

Revision ID: 2d9a25777f24
Revises: c0523f1f6d99
Create Date: 2026-08-17 01:16:00.416420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d9a25777f24'
down_revision: Union[str, Sequence[str], None] = 'c0523f1f6d99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="job_seeker"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role")