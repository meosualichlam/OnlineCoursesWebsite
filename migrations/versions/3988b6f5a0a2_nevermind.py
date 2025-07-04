"""Nevermind

Revision ID: 3988b6f5a0a2
Revises: 9250e7cb85c2
Create Date: 2025-05-09 22:25:44.174297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3988b6f5a0a2'
down_revision = '9250e7cb85c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('video_url', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('video_url')
        batch_op.drop_column('duration')
        batch_op.drop_column('description')

    # ### end Alembic commands ###
