"""Add auto-update timestamp

Revision ID: 298f37df5867
Revises: 26bfcda90ac6
Create Date: 2021-08-03 13:17:46.365113

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '298f37df5867'
down_revision = '26bfcda90ac6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_descriptors_last_updated', table_name='user_descriptors')
    op.drop_column('user_descriptors', 'last_updated')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_descriptors', sa.Column('last_updated', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.create_index('ix_user_descriptors_last_updated', 'user_descriptors', ['last_updated'], unique=False)
    # ### end Alembic commands ###