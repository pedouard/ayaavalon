import sqlalchemy as sa
import sqlalchemy.ext.declarative
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.pool import NullPool
from sqlalchemy.sql.expression import func
from withings.datascience.core import config
from withings.datascience.core.sqlalchemy_utils import JSON
from sqlalchemy.schema import ForeignKey
from ayaavalon.constants import *


Base = sa.ext.declarative.declarative_base()
config_section = 'ayaavalon'


def info():
    """Called by alembic/env.py
    """
    db_uri = config.get(config_section, 'db_uri')
    return db_uri, Base.metadata


def create_session():
    """Return a scoped session.
    """
    global _Session, engine
    if _Session is None:
        db_uri, _ = info()
        engine = sa.create_engine(db_uri, poolclass=NullPool)
        _Session = sa.orm.scoped_session(sa.orm.sessionmaker(bind=engine))
    return _Session()

_Session = None
engine = None
session = create_session()


class Player(Base):
    __tablename__ = "player"

    id_player = Column(Integer, primary_key=True)

    userid_player = Column(Integer, nullable=False, unique=True)
    info_player = Column(JSON, nullable=False)

    url_64_player = Column(String, default=None, nullable=True)
    url_128_player = Column(String, default=None, nullable=True)
    url_256_player = Column(String, default=None, nullable=True)

    created_player = Column(DateTime, default=func.now(), nullable=False)
    modified_player = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, userid, info, url_64=None, url_128=None, url_256=None):
        self.userid_player = userid
        self.info_player = info

        self.url_64_player = url_64
        self.url_128_player = url_128
        self.url_256_player = url_256


class Game(Base):
    __tablename__ = "game"

    id_game = Column(Integer, primary_key=True)
    version_game = Column(Integer, nullable=False)

    info_game = Column(JSON, nullable=False)

    created_game = Column(DateTime, default=func.now(), nullable=False)
    modified_game = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, info, version):
        self.info_game = info
        self.version_game = version


class GameStats(Base):
    __tablename__ = "gamestats"

    id_gamestats = Column(Integer, primary_key=True)

    id_game = Column(Integer, ForeignKey('game.id_game'))
    host = Column(Integer, ForeignKey('player.id_player'))
    n_players = Column(Integer)

    good_wins = Column(Boolean, nullable=False)
    merlin_killed = Column(Boolean)
    merlin_targeted = Column(Integer, ForeignKey('player.id_player'))

    merlin = Column(Integer, ForeignKey('player.id_player'))
    perceval = Column(Integer, ForeignKey('player.id_player'))
    galahad = Column(Integer, ForeignKey('player.id_player'))
    mordred = Column(Integer, ForeignKey('player.id_player'))
    morgana = Column(Integer, ForeignKey('player.id_player'))
    oberon = Column(Integer, ForeignKey('player.id_player'))
    assassin = Column(Integer, ForeignKey('player.id_player'))

    @staticmethod
    def from_game(game):
        if type(game) != Game:
            raise TypeError('argument should be a Game record.')

        info = game.info_game
        print(info)

        player_roles = {}
        for role in [MERLIN, PERCI, GALAHAD, MORDRED, MORGANA, ASSASSIN, OBERON]:
            for player, player_role in zip(info['players'], info['roles']):
                if role == player_role:
                    player_roles[role] = player
                    break
            else:
                player_roles[role] = None

        gs = GameStats(
            id_game=game.id_game,
            host=info['host'],
            n_players=len(info['players']),

            good_wins=info['good_wins'],
            merlin_killed=info['merlin_killed'],
            merlin_targeted=info['merlin_targeted'],

            merlin=player_roles[MERLIN],
            perceval=player_roles[PERCI],
            galahad=player_roles[GALAHAD],
            mordred=player_roles[MORDRED],
            morgana=player_roles[MORGANA],
            oberon=player_roles[ASSASSIN],
            assassin=player_roles[OBERON],
        )

        return gs

# def update_rankings():
#     ps = PlayerStats.objects
#
#     ratings = {tri[0]: trueskill.Rating() for tri in Player.objects.values_list('tri')}
#     ratings['EVI'] = trueskill.Rating(55)
#     ratings['GOO'] = trueskill.Rating(-5)
#     for game in GameStats.objects.all().order_by('game__date'):
#         evil_tri = game.evil_team_tri + ',EVI'
#         good_tri = game.good_team_tri + ',GOO'
#         evil_team = [ratings[tri] for tri in evil_tri.split(',')]
#         good_team = [ratings[tri] for tri in good_tri.split(',')]
#         rank = int(game.good_win)
#         # lower rank is better
#         new_evil_rating, new_good_rating = trueskill.rate([evil_team, good_team], ranks=[rank, 1-rank])
#         for new_rating, trigram in zip(new_evil_rating, evil_tri.split(',')):
#             ratings[trigram] = new_rating
#         for new_rating, trigram in zip(new_good_rating, good_tri.split(',')):
#             ratings[trigram] = new_rating
#
#     for tri, rating in ratings.items():
#         ps.filter(player__tri=tri).update(ranking_trueskill=float(rating))
#
#     # dummy player objects
#     Player.objects.get_or_create(tri='EVI')
#     Player.objects.get_or_create(tri='GOO')
#     player, created = Player.objects.update_or_create(tri='EVI', defaults={'stats__ranking_trueskill': float(ratings['EVI'])})
#     player, created = Player.objects.update_or_create(tri='GOO', defaults={'stats__ranking_trueskill': float(ratings['GOO'])})
#
#     print('Evil ranking:', ratings['EVI'])
#     print('Good ranking:', ratings['GOO'])