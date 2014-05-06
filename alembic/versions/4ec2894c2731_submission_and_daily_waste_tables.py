"""submission and daily waste tables

Revision ID: 4ec2894c2731
Revises: None
Create Date: 2014-05-06 10:53:05.112025

"""

# revision identifiers, used by Alembic.
revision = '4ec2894c2731'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('submissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('xform_id', sa.String(length=100), nullable=False),
    sa.Column('json_data', postgresql.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_xform_id'), 'submissions', ['xform_id'], unique=False)
    op.create_table('daily_wastes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('submission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('daily_wastes')
    op.drop_index(op.f('ix_submissions_xform_id'), table_name='submissions')
    op.drop_table('submissions')
    ### end Alembic commands ###
