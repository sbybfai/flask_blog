"""post add title

Revision ID: 3b6197dcef2b
Revises: 832b38cb577d
Create Date: 2019-01-19 19:15:54.715926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b6197dcef2b'
down_revision = '832b38cb577d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('title', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'title')
    # ### end Alembic commands ###
