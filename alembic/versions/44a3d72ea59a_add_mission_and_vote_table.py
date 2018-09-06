"""add mission and vote table

Revision ID: 44a3d72ea59a
Revises: 217232acbf89
Create Date: 2018-09-05 14:01:08.560426

"""

# revision identifiers, used by Alembic.
revision = '44a3d72ea59a'
down_revision = '217232acbf89'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mission',
    sa.Column('id_mission', sa.Integer(), nullable=False),
    sa.Column('id_game', sa.Integer(), nullable=True),
    sa.Column('arthur', sa.Integer(), nullable=True),
    sa.Column('turn', sa.Integer(), nullable=True),
    sa.Column('mission', sa.Integer(), nullable=True),
    sa.Column('accepted', sa.Boolean(), nullable=True),
    sa.Column('imposed', sa.Boolean(), nullable=True),
    sa.Column('succeded', sa.Boolean(), nullable=True),
    sa.Column('n_fails', sa.Integer(), nullable=True),
    sa.Column('n_success', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['arthur'], ['player.userid_player'], ),
    sa.ForeignKeyConstraint(['id_game'], ['game.id_game'], ),
    sa.PrimaryKeyConstraint('id_mission')
    )
    op.create_table('vote',
    sa.Column('id_vote', sa.Integer(), nullable=False),
    sa.Column('id_mission', sa.Integer(), nullable=True),
    sa.Column('id_player', sa.Integer(), nullable=True),
    sa.Column('id_target', sa.Integer(), nullable=True),
    sa.Column('vote', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['id_mission'], ['mission.id_mission'], ),
    sa.ForeignKeyConstraint(['id_player'], ['player.userid_player'], ),
    sa.ForeignKeyConstraint(['id_target'], ['player.userid_player'], ),
    sa.PrimaryKeyConstraint('id_vote')
    )
    op.drop_column('role', 'has_won')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('has_won', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_table('vote')
    op.drop_table('mission')
    # ### end Alembic commands ###