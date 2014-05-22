"""municipality_submission table

Revision ID: 69903951dae
Revises: 4d046bfb2b66
Create Date: 2014-05-22 11:22:10.928044

"""

# revision identifiers, used by Alembic.
revision = '69903951dae'
down_revision = '4d046bfb2b66'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'municipality_submissions',
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('municipality_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['municipality_id'], ['municipalities.id'], ),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
        sa.PrimaryKeyConstraint('submission_id')
    )
    op.create_index(op.f('ix_municipality_id_submission_id'), 'municipality_submissions', ['municipality_id', 'submission_id'], unique=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_municipality_id_submission_id'), table_name='municipality_submissions')
    op.drop_table('municipality_submissions')
    ### end Alembic commands ###
