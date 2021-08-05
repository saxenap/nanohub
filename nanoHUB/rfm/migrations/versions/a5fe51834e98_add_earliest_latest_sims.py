"""add earliest latest sims

Revision ID: a5fe51834e98
Revises: e9a051d41bba
Create Date: 2021-08-04 15:05:45.044954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5fe51834e98'
down_revision = 'e9a051d41bba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_descriptors', sa.Column('username', sa.String(length=150), nullable=True))
    op.add_column('user_descriptors', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('user_descriptors', sa.Column('email', sa.String(length=150), nullable=True))
    op.add_column('user_descriptors', sa.Column('earliest_simulation', sa.DateTime(), nullable=True))
    op.add_column('user_descriptors', sa.Column('latest_simulation', sa.DateTime(), nullable=True))
    op.add_column('user_descriptors', sa.Column('simulation_lifetime_days', sa.Integer(), nullable=True))
    op.add_column('user_descriptors', sa.Column('simulations_run_count', sa.Integer(), nullable=True))
    op.add_column('user_descriptors', sa.Column('tools_used_names', sa.Text(), nullable=True))
    op.add_column('user_descriptors', sa.Column('tools_used_count', sa.Integer(), nullable=True))
    op.add_column('user_descriptors', sa.Column('days_spent_on_nanohub', sa.Integer(), nullable=True, comment='total number of days spent on nanoHUB'))
    op.add_column('user_descriptors', sa.Column('user_lifetime_days', sa.Integer(), nullable=True, comment='last day - registration day'))
    op.add_column('user_descriptors', sa.Column('average_freqency', sa.Numeric(), nullable=True, comment='F = lifetime in days / Days spent on nanoHUB'))
    op.add_column('user_descriptors', sa.Column('registerDate', sa.DateTime(), nullable=True))
    op.add_column('user_descriptors', sa.Column('lastvisitDate', sa.DateTime(), nullable=True))
    op.add_column('user_descriptors', sa.Column('timestamp_last_updated', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('user_descriptors', sa.Column('timestamp_created', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_user_descriptors_average_freqency'), 'user_descriptors', ['average_freqency'], unique=False)
    op.create_index(op.f('ix_user_descriptors_earliest_simulation'), 'user_descriptors', ['earliest_simulation'], unique=False)
    op.create_index(op.f('ix_user_descriptors_lastvisitDate'), 'user_descriptors', ['lastvisitDate'], unique=False)
    op.create_index(op.f('ix_user_descriptors_latest_simulation'), 'user_descriptors', ['latest_simulation'], unique=False)
    op.create_index(op.f('ix_user_descriptors_registerDate'), 'user_descriptors', ['registerDate'], unique=False)
    op.create_index(op.f('ix_user_descriptors_timestamp_last_updated'), 'user_descriptors', ['timestamp_last_updated'], unique=False)
    op.create_unique_constraint(None, 'user_descriptors', ['username'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_descriptors', type_='unique')
    op.drop_index(op.f('ix_user_descriptors_timestamp_last_updated'), table_name='user_descriptors')
    op.drop_index(op.f('ix_user_descriptors_registerDate'), table_name='user_descriptors')
    op.drop_index(op.f('ix_user_descriptors_latest_simulation'), table_name='user_descriptors')
    op.drop_index(op.f('ix_user_descriptors_lastvisitDate'), table_name='user_descriptors')
    op.drop_index(op.f('ix_user_descriptors_earliest_simulation'), table_name='user_descriptors')
    op.drop_index(op.f('ix_user_descriptors_average_freqency'), table_name='user_descriptors')
    op.drop_column('user_descriptors', 'timestamp_created')
    op.drop_column('user_descriptors', 'timestamp_last_updated')
    op.drop_column('user_descriptors', 'lastvisitDate')
    op.drop_column('user_descriptors', 'registerDate')
    op.drop_column('user_descriptors', 'average_freqency')
    op.drop_column('user_descriptors', 'user_lifetime_days')
    op.drop_column('user_descriptors', 'days_spent_on_nanohub')
    op.drop_column('user_descriptors', 'tools_used_count')
    op.drop_column('user_descriptors', 'tools_used_names')
    op.drop_column('user_descriptors', 'simulations_run_count')
    op.drop_column('user_descriptors', 'simulation_lifetime_days')
    op.drop_column('user_descriptors', 'latest_simulation')
    op.drop_column('user_descriptors', 'earliest_simulation')
    op.drop_column('user_descriptors', 'email')
    op.drop_column('user_descriptors', 'name')
    op.drop_column('user_descriptors', 'username')
    # ### end Alembic commands ###
