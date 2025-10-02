"""add questions column to rooms

Revision ID: 2c0bceac9e7a
Revises: 
Create Date: 2025-09-30 16:02:30.238464

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c0bceac9e7a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add questions column to rooms table
    op.add_column('rooms', sa.Column('questions', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove questions column from rooms table
    op.drop_column('rooms', 'questions')