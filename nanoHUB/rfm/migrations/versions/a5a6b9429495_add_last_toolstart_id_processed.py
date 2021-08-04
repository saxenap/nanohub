"""add last_toolstart_id_processed

Revision ID: a5a6b9429495
Revises: 1076004dddd8
Create Date: 2021-08-04 09:43:04.428660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5a6b9429495'
down_revision = '1076004dddd8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_descriptors', sa.Column('last_toolstart_id_processed', sa.BigInteger(), nullable=False))
    op.create_index(op.f('ix_user_descriptors_last_toolstart_id_processed'), 'user_descriptors', ['last_toolstart_id_processed'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_descriptors_last_toolstart_id_processed'), table_name='user_descriptors')
    op.drop_column('user_descriptors', 'last_toolstart_id_processed')
    # ### end Alembic commands ###