"""merge migration heads

Revision ID: c318404915cf
Revises: 1dbffb426a9b, 514397005bdf
Create Date: 2026-08-27 16:58:26.329954

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c318404915cf'
down_revision: Union[str, None] = ('1dbffb426a9b', '514397005bdf')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No-op: a merge revision only reconciles divergent branches in the Alembic
    # graph; it introduces no schema change of its own.
    pass


def downgrade() -> None:
    # No-op: reverting the merge simply restores the two independent heads; there
    # is no schema change to undo here.
    pass
