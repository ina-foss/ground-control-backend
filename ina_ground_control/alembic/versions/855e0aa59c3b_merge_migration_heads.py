"""Merge migration heads

Revision ID: 855e0aa59c3b
Revises: 109d06e40f9b, 6752eb34f10e
Create Date: 2026-07-01 15:45:39.025380

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '855e0aa59c3b'
down_revision: Union[str, None] = ('109d06e40f9b', '6752eb34f10e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
