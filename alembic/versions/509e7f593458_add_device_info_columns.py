"""Add device info columns

Revision ID: 509e7f593458
Revises: a07a0bc9cbcc
Create Date: 2018-03-09 14:43:03.660375

"""

# revision identifiers, used by Alembic.
revision = '509e7f593458'
down_revision = 'a07a0bc9cbcc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('deviceid_player', sa.Integer(), nullable=False))
    op.add_column('player', sa.Column('mac_player', sa.String(), nullable=False))
    op.add_column('player', sa.Column('previous_deploy_grp_player', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'previous_deploy_grp_player')
    op.drop_column('player', 'mac_player')
    op.drop_column('player', 'deviceid_player')
    # ### end Alembic commands ###
