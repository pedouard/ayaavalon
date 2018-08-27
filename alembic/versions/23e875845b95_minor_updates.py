"""Minor updates

Revision ID: 23e875845b95
Revises: 76cf4b156836
Create Date: 2018-02-03 18:01:51.427002

"""

# revision identifiers, used by Alembic.
revision = '23e875845b95'
down_revision = '76cf4b156836'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contract', sa.Column('is_active_contract', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contract', 'is_active_contract')
    # ### end Alembic commands ###