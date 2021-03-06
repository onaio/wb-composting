"""added group field to users

Revision ID: 9b5f079184b
Revises: 47e593b61a6d
Create Date: 2014-06-17 15:08:57.374612

"""

# revision identifiers, used by Alembic.
revision = '9b5f079184b'
down_revision = '47e593b61a6d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('group', sa.String(), server_default='sm', nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'group')
    ### end Alembic commands ###
