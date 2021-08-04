"""default value last_toolstart_id_processed

Revision ID: 8cce1471fa6d
Revises: a5a6b9429495
Create Date: 2021-08-04 10:56:41.103990

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8cce1471fa6d'
down_revision = 'a5a6b9429495'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_descriptors_average_freqency_last_updated', table_name='user_descriptors')
    op.drop_index('ix_user_descriptors_simulation_lifetime_days_last_updated', table_name='user_descriptors')
    op.drop_index('ix_user_descriptors_simulations_run_count_last_updated', table_name='user_descriptors')
    op.drop_index('ix_user_descriptors_tools_used_count_last_updated', table_name='user_descriptors')
    op.drop_index('ix_user_descriptors_tools_used_names_last_updated', table_name='user_descriptors')
    op.drop_column('user_descriptors', 'tools_used_names_last_updated')
    op.drop_column('user_descriptors', 'tools_used_count_last_updated')
    op.drop_column('user_descriptors', 'simulations_run_count_last_updated')
    op.drop_column('user_descriptors', 'simulation_lifetime_days_last_updated')
    op.drop_column('user_descriptors', 'average_freqency_last_updated')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_descriptors', sa.Column('average_freqency_last_updated', mysql.DATETIME(), server_default=sa.text("'1970-01-02 00:00:00'"), nullable=False))
    op.add_column('user_descriptors', sa.Column('simulation_lifetime_days_last_updated', mysql.DATETIME(), server_default=sa.text("'1970-01-02 00:00:00'"), nullable=False))
    op.add_column('user_descriptors', sa.Column('simulations_run_count_last_updated', mysql.DATETIME(), server_default=sa.text("'1970-01-02 00:00:00'"), nullable=False))
    op.add_column('user_descriptors', sa.Column('tools_used_count_last_updated', mysql.DATETIME(), server_default=sa.text("'1970-01-02 00:00:00'"), nullable=False))
    op.add_column('user_descriptors', sa.Column('tools_used_names_last_updated', mysql.DATETIME(), server_default=sa.text("'1970-01-02 00:00:00'"), nullable=False))
    op.create_index('ix_user_descriptors_tools_used_names_last_updated', 'user_descriptors', ['tools_used_names_last_updated'], unique=False)
    op.create_index('ix_user_descriptors_tools_used_count_last_updated', 'user_descriptors', ['tools_used_count_last_updated'], unique=False)
    op.create_index('ix_user_descriptors_simulations_run_count_last_updated', 'user_descriptors', ['simulations_run_count_last_updated'], unique=False)
    op.create_index('ix_user_descriptors_simulation_lifetime_days_last_updated', 'user_descriptors', ['simulation_lifetime_days_last_updated'], unique=False)
    op.create_index('ix_user_descriptors_average_freqency_last_updated', 'user_descriptors', ['average_freqency_last_updated'], unique=False)
    # ### end Alembic commands ###