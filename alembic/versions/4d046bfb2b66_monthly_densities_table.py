"""monthly_densities table

Revision ID: 4d046bfb2b66
Revises: 4fd864c45f09
Create Date: 2014-05-19 15:04:58.556550

"""

# revision identifiers, used by Alembic.
revision = '4d046bfb2b66'
down_revision = '4fd864c45f09'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('submissions', sa.Column('submission_type', sa.String(length=50), server_default='submission', nullable=False))
    op.create_index(op.f('ix_submissions_submission_type'), 'submissions', ['submission_type'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_submissions_submission_type'), table_name='submissions')
    op.drop_column('submissions', 'submission_type')
    ### end Alembic commands ###
