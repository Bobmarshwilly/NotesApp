"""Email was added to 'users' table

Revision ID: 80adf5dfab3b
Revises: 6c53b88cca9a
Create Date: 2025-06-25 00:16:59.760487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80adf5dfab3b'
down_revision: Union[str, None] = '6c53b88cca9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.execute("UPDATE users SET email = 'default@email.com' WHERE email IS NULL")
    op.alter_column('users', 'email', nullable=False)
    op.create_unique_constraint("unique_users_email", 'users', ['email'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("unique_users_email", 'users', type_='unique')
    op.drop_column('users', 'email')
