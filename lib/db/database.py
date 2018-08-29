import sqlalchemy as sa

from sqlalchemy import Column, Integer, String, Index, DateTime, Boolean
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import func

from withings.datascience.core.sqlalchemy_utils import JSON
from withings.datascience.core import config

Base = sa.ext.declarative.declarative_base()
config_section = 'ayaavalon'

def info():
    """Called by alembic/env.py
    """
    db_uri = config.get(config_section, 'db_uri')
    return db_uri, Base.metadata

def session():
    """Return a scoped session.
    """
    global _Session
    if _Session is None:
        db_uri, _ = info()
        engine = sa.create_engine(db_uri, poolclass=NullPool)
        _Session = sa.orm.scoped_session(sa.orm.sessionmaker(bind=engine))
    return _Session()
_Session = None


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

    def __init__(self, info):
        self.info_game = info

