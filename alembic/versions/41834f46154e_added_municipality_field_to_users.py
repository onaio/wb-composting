"""added municipality field to users

Revision ID: 41834f46154e
Revises: 9b5f079184b
Create Date: 2014-06-17 16:12:38.370192

"""

# revision identifiers, used by Alembic.
revision = '41834f46154e'
down_revision = '9b5f079184b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('municipality_id', sa.Integer(), nullable=True))
    op.create_foreign_key("fk_municipality_user", "users", "municipalities", ["municipality_id"], ["id"])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_municipality_user', 'users', 'foreignkey')
    op.drop_column('users', 'municipality_id')
    ### end Alembic commands ###
