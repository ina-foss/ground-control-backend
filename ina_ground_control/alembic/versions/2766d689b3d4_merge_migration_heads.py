"""merge migration heads

Revision ID: 2766d689b3d4
Revises: 5940cdd6d66d, 80beb50daf87
Create Date: 2026-08-17 14:56:23.810923

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2766d689b3d4'
down_revision: Union[str, None] = ('5940cdd6d66d', '80beb50daf87')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
