"""windrow monitoring table

Revision ID: 284ec1ec97ae
Revises: 3a28bde53cbe
Create Date: 2014-06-06 12:02:12.657476

"""

# revision identifiers, used by Alembic.
revision = '284ec1ec97ae'
down_revision = '3a28bde53cbe'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('windrow_monitorings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('windrow_no', sa.String(length=100), nullable=False),
    sa.Column('week_no', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['submissions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_windrow_monitorings_week_no'), 'windrow_monitorings', ['week_no'], unique=False)
    op.create_index(op.f('ix_windrow_monitorings_windrow_no'), 'windrow_monitorings', ['windrow_no'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_windrow_monitorings_windrow_no'), table_name='windrow_monitorings')
    op.drop_index(op.f('ix_windrow_monitorings_week_no'), table_name='windrow_monitorings')
    op.drop_table('windrow_monitorings')
    ### end Alembic commands ###