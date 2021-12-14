"""add start_time to show table

Revision ID: 943a8e70c634
Revises: 15c282a3a190
Create Date: 2021-12-14 15:56:15.837941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '943a8e70c634'
down_revision = '15c282a3a190'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('start_time', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('show', 'start_time')
    # ### end Alembic commands ###
