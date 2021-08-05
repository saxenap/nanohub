"""update class LastUpdateRecord

Revision ID: 026ac09cdfde
Revises: 89b7ce13bc5d
Create Date: 2021-08-04 12:30:34.339848

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '026ac09cdfde'
down_revision = '89b7ce13bc5d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_last_update_record_timestamp_last_updated', table_name='last_update_record')
    op.drop_index('ix_last_update_record_last_processed_toolstart_id', table_name='last_update_record')
    op.create_index(op.f('ix_last_update_record_last_processed_toolstart_id'), 'last_update_record', ['last_processed_toolstart_id'], unique=True)
    op.drop_column('last_update_record', 'timestamp_last_updated')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('last_update_record', sa.Column('timestamp_last_updated', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False))
    op.drop_index(op.f('ix_last_update_record_last_processed_toolstart_id'), table_name='last_update_record')
    op.create_index('ix_last_update_record_last_processed_toolstart_id', 'last_update_record', ['last_processed_toolstart_id'], unique=False)
    op.create_index('ix_last_update_record_timestamp_last_updated', 'last_update_record', ['timestamp_last_updated'], unique=False)
    # ### end Alembic commands ###
