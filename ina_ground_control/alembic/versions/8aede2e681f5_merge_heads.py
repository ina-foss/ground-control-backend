"""merge heads

Revision ID: 8aede2e681f5
Revises: 3e6bf3810879, 909cbfdf5e93
Create Date: 2026-04-20 17:49:45.330854

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8aede2e681f5'
down_revision: Union[str, None] = ('3e6bf3810879', '909cbfdf5e93')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration - no operation required"""
    pass


def downgrade() -> None:
    """Merge migration - no operation required"""
    pass
