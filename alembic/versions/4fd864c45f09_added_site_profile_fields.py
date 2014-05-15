"""added site profile fields

Revision ID: 4fd864c45f09
Revises: 241611952129
Create Date: 2014-05-15 12:34:16.091892

"""

# revision identifiers, used by Alembic.
revision = '4fd864c45f09'
down_revision = '241611952129'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('municipalities', sa.Column('box_volume', sa.Float(), server_default='0.125', nullable=False))
    op.add_column('municipalities', sa.Column('leachete_tank_length', sa.Float(), server_default='5.0', nullable=False))
    op.add_column('municipalities', sa.Column('leachete_tank_width', sa.Float(), server_default='5.0', nullable=False))
    op.add_column('municipalities', sa.Column('wheelbarrow_volume', sa.Float(), server_default='0.625', nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('municipalities', 'wheelbarrow_volume')
    op.drop_column('municipalities', 'leachete_tank_width')
    op.drop_column('municipalities', 'leachete_tank_length')
    op.drop_column('municipalities', 'box_volume')
    ### end Alembic commands ###
