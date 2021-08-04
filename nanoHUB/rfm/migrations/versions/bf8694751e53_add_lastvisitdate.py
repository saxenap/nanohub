"""Add lastvisitDate

Revision ID: bf8694751e53
Revises: 4465582f52c9
Create Date: 2021-08-02 21:04:20.729215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf8694751e53'
down_revision = '4465582f52c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_descriptors', sa.Column('lastvisitDate', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_user_descriptors_lastvisitDate'), 'user_descriptors', ['lastvisitDate'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_descriptors_lastvisitDate'), table_name='user_descriptors')
    op.drop_column('user_descriptors', 'lastvisitDate')
    # ### end Alembic commands ###