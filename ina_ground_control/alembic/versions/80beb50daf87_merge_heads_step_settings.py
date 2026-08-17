"""Merge migration heads (typed step settings + previous merge)

Revision ID: 80beb50daf87
Revises: 855e0aa59c3b, b3bc57fab2ab
Create Date: 2026-08-04 00:00:00.000000

No-op merge unifying the two remaining Alembic heads into a single head so
``alembic upgrade head`` resolves unambiguously.
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "80beb50daf87"
down_revision: Union[str, Sequence[str], None] = ("855e0aa59c3b", "b3bc57fab2ab")
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
