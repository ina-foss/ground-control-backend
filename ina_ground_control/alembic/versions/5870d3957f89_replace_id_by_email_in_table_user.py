""" replace 'id' by 'email' in table user

Revision ID: 5870d3957f89
Revises: d9a0eace8672
Create Date: 2024-06-13 14:30:41.321485

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5870d3957f89'
down_revision: Union[str, None] = 'd9a0eace8672'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the new column to annotation table
    op.add_column('annotation', sa.Column(
        'user_email', sa.String(), nullable=False))

    # Drop the existing foreign key constraint on annotation table
    op.drop_constraint('annotation_user_id_fkey',
                       'annotation', type_='foreignkey')

    # Drop the old user_id column from annotation table
    op.drop_column('annotation', 'user_id')

    # Drop the existing foreign key constraint on project table
    op.drop_constraint('project_created_by_fkey',
                       'project', type_='foreignkey')

    # Alter project table to change created_by column type from Integer to String
    op.alter_column('project', 'created_by',
                    existing_type=sa.INTEGER(),
                    type_=sa.String(),
                    existing_nullable=True)

    # Ensure the email column in user table is non-nullable
    op.alter_column('user', 'email',
                    existing_type=sa.VARCHAR(),
                    nullable=False)

    # Add unique constraint to the email column
    op.create_unique_constraint('uq_user_email', 'user', ['email'])

    op.create_foreign_key('annotation_user_email_fkey',
                          'annotation', 'user', ['user_email'], ['email'])

    # Create a new foreign key constraint for project table referencing user.email
    op.create_foreign_key('fk_project_created_by_user_email',
                          'project', 'user', ['created_by'], ['email'])

    # Drop the id column from user table since email is primary key
    op.drop_column('user', 'id')


def downgrade():
    # Drop the new foreign key constraint on project table
    op.drop_constraint('fk_project_created_by_user_email',
                       'project', type_='foreignkey')

    # Change the created_by column back to Integer in project table
    op.alter_column('project', 'created_by',
                    existing_type=sa.String(),
                    type_=sa.INTEGER(),
                    existing_nullable=True)

    # Recreate the original foreign key constraint on project table
    op.create_foreign_key('project_created_by_fkey',
                          'project', 'user', ['created_by'], ['id'])

    # Recreate the id column in user table
    op.add_column('user', sa.Column('id', sa.INTEGER(),
                                    autoincrement=True, nullable=False))

    # Ensure email is nullable again and drop the unique constraint
    op.alter_column('user', 'email',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.drop_constraint('uq_user_email', 'user', type_='unique')

    # Recreate the user_id column in annotation table
    op.add_column('annotation', sa.Column(
        'user_id', sa.INTEGER(), nullable=True))

    # Drop the user_email column from annotation table
    op.drop_column('annotation', 'user_email')

    # Recreate the original foreign key constraint on annotation table
    op.create_foreign_key('annotation_user_id_fkey',
                          'annotation', 'user', ['user_id'], ['id'])
