"""add description/student_id column

Revision ID: f6bb55b66fc2
Revises: a9d1f95c6cfb
Create Date: 2024-08-11 19:09:29.642025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6bb55b66fc2'
down_revision = 'a9d1f95c6cfb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('trans_for', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('user_description', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('desc', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_column('desc')
        batch_op.drop_column('user_description')
        batch_op.drop_column('trans_for')

    # ### end Alembic commands ###
