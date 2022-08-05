"""Add unique to algorithm name

Revision ID: e79931189298
Revises: da39de5920a6
Create Date: 2022-06-16 22:15:47.170262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e79931189298'
down_revision = 'da39de5920a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'algorithm_info', ['name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'algorithm_info', type_='unique')
    # ### end Alembic commands ###