"""set default datetime 5

Revision ID: a1ceb73a2581
Revises: 94961cbb94c5
Create Date: 2021-08-03 21:25:55.770459

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a1ceb73a2581'
down_revision = '94961cbb94c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_descriptors_average_freqency_last_updated', table_name='user_descriptors')
    op.drop_index('ix_user_descriptors_simulation_lifetime_days_last_updated', table_name='user_descriptors')
    op.drop_index('ix_user_descriptors_simulations_run_count_last_updated', table_name='user_descriptors')
    op.drop_index('ix_user_descriptors_tools_used_count_last_updated', table_name='user_descriptors')
    op.drop_index('ix_user_descriptors_tools_used_names_last_updated', table_name='user_descriptors')
    op.drop_column('user_descriptors', 'tools_used_count_last_updated')
    op.drop_column('user_descriptors', 'tools_used_names_last_updated')
    op.drop_column('user_descriptors', 'simulation_lifetime_days_last_updated')
    op.drop_column('user_descriptors', 'simulations_run_count_last_updated')
    op.drop_column('user_descriptors', 'average_freqency_last_updated')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_descriptors', sa.Column('average_freqency_last_updated', mysql.DATETIME(), nullable=False))
    op.add_column('user_descriptors', sa.Column('simulations_run_count_last_updated', mysql.DATETIME(), nullable=False))
    op.add_column('user_descriptors', sa.Column('simulation_lifetime_days_last_updated', mysql.DATETIME(), nullable=False))
    op.add_column('user_descriptors', sa.Column('tools_used_names_last_updated', mysql.DATETIME(), nullable=False))
    op.add_column('user_descriptors', sa.Column('tools_used_count_last_updated', mysql.DATETIME(), nullable=False))
    op.create_index('ix_user_descriptors_tools_used_names_last_updated', 'user_descriptors', ['tools_used_names_last_updated'], unique=False)
    op.create_index('ix_user_descriptors_tools_used_count_last_updated', 'user_descriptors', ['tools_used_count_last_updated'], unique=False)
    op.create_index('ix_user_descriptors_simulations_run_count_last_updated', 'user_descriptors', ['simulations_run_count_last_updated'], unique=False)
    op.create_index('ix_user_descriptors_simulation_lifetime_days_last_updated', 'user_descriptors', ['simulation_lifetime_days_last_updated'], unique=False)
    op.create_index('ix_user_descriptors_average_freqency_last_updated', 'user_descriptors', ['average_freqency_last_updated'], unique=False)
    # ### end Alembic commands ###
