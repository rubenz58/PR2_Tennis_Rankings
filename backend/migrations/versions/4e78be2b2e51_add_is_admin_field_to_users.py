"""Add is_admin field to users

Revision ID: 4e78be2b2e51
Revises: 151f8fc061c6
Create Date: 2025-08-19 15:52:40.528006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e78be2b2e51'
down_revision = '151f8fc061c6'
branch_labels = None
depends_on = None


def upgrade():
    # Add the column as nullable first
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))
    
    # Set default value for existing users
    op.execute("UPDATE users SET is_admin = false WHERE is_admin IS NULL")
    
    # Now make it non-nullable
    op.alter_column('users', 'is_admin', nullable=False)

def downgrade():
    op.drop_column('users', 'is_admin')

    # ### end Alembic commands ###
