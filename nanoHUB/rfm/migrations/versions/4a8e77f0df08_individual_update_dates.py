"""individual update dates

Revision ID: 4a8e77f0df08
Revises: fd274a13bca4
Create Date: 2021-08-03 20:10:08.221105

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a8e77f0df08'
down_revision = 'fd274a13bca4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_descriptors', sa.Column('simulations_last_updated', sa.DateTime(), nullable=False))
    op.add_column('user_descriptors', sa.Column('name_tools_used_last_updated', sa.DateTime(), nullable=False))
    op.add_column('user_descriptors', sa.Column('num_tools_last_updated', sa.DateTime(), nullable=False))
    op.add_column('user_descriptors', sa.Column('average_freqency_last_updated', sa.DateTime(), nullable=False))
    op.create_index(op.f('ix_user_descriptors_average_freqency_last_updated'), 'user_descriptors', ['average_freqency_last_updated'], unique=False)
    op.create_index(op.f('ix_user_descriptors_name_tools_used_last_updated'), 'user_descriptors', ['name_tools_used_last_updated'], unique=False)
    op.create_index(op.f('ix_user_descriptors_num_tools_last_updated'), 'user_descriptors', ['num_tools_last_updated'], unique=False)
    op.create_index(op.f('ix_user_descriptors_simulations_last_updated'), 'user_descriptors', ['simulations_last_updated'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_descriptors_simulations_last_updated'), table_name='user_descriptors')
    op.drop_index(op.f('ix_user_descriptors_num_tools_last_updated'), table_name='user_descriptors')
    op.drop_index(op.f('ix_user_descriptors_name_tools_used_last_updated'), table_name='user_descriptors')
    op.drop_index(op.f('ix_user_descriptors_average_freqency_last_updated'), table_name='user_descriptors')
    op.drop_column('user_descriptors', 'average_freqency_last_updated')
    op.drop_column('user_descriptors', 'num_tools_last_updated')
    op.drop_column('user_descriptors', 'name_tools_used_last_updated')
    op.drop_column('user_descriptors', 'simulations_last_updated')
    # ### end Alembic commands ###
