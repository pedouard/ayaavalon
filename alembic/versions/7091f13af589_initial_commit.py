"""Initial commit

Revision ID: 7091f13af589
Revises:
Create Date: 2018-08-27 17:32:42.344614

"""

# revision identifiers, used by Alembic.
revision = '7091f13af589'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import withings

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game',
    sa.Column('id_game', sa.Integer(), nullable=False),
    sa.Column('info_game', withings.datascience.core.sqlalchemy_utils.JSONEncodedDict(), nullable=False),
    sa.Column('created_game', sa.DateTime(), nullable=False),
    sa.Column('modified_game', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id_game')
    )
    op.create_table('player',
    sa.Column('id_player', sa.Integer(), nullable=False),
    sa.Column('userid_player', sa.Integer(), nullable=False),
    sa.Column('info_player', withings.datascience.core.sqlalchemy_utils.JSONEncodedDict(), nullable=False),
    sa.Column('url_64_player', sa.String(), nullable=True),
    sa.Column('url_128_player', sa.String(), nullable=True),
    sa.Column('url_256_player', sa.String(), nullable=True),
    sa.Column('created_player', sa.DateTime(), nullable=False),
    sa.Column('modified_player', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id_player'),
    sa.UniqueConstraint('userid_player')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('player')
    op.drop_table('game')
    ### end Alembic commands ###
