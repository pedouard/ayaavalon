import sqlalchemy as sa

from sqlalchemy import Column, Integer, String, Index, DateTime, Boolean
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import func

from withings.datascience.core.sqlalchemy_utils import JSON
from withings.datascience.core import config

Base = sa.ext.declarative.declarative_base()
config_section = 'ayaa'

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
    is_active_player = Column(Boolean, default=True, nullable=False)
    is_ios_player = Column(Boolean, default=False, nullable=False)

    token_player = Column(String, nullable=False)

    is_alive_player = Column(Boolean, default=False, nullable=False)
    total_points_player = Column(Integer, default=0, nullable=False)
    round_points_player = Column(Integer, default=0, nullable=False)

    deviceid_player = Column(Integer, nullable=False)
    previous_deploy_grp_player = Column(Integer, nullable=False)
    mac_player = Column(String, nullable=False)

    url_64_player = Column(String, default=None, nullable=True)
    url_128_player = Column(String, default=None, nullable=True)
    url_256_player = Column(String, default=None, nullable=True)

    created_player = Column(DateTime, default=func.now(), nullable=False)
    modified_player = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, userid, info, token, deviceid, mac, deploy_grp,
                 url_64=None, url_128=None, url_256=None, is_active=True,
                 is_alive=False):
        self.userid_player = userid
        self.info_player = info
        self.token_player = token

        self.deviceid_player = deviceid
        self.previous_deploy_grp_player = deploy_grp
        self.mac_player = mac

        self.url_64_player = url_64
        self.url_128_player = url_128
        self.url_256_player = url_256

        self.is_active_player = is_active
        self.is_alive_player = is_alive

class Contract(Base):
    __tablename__ = "contract"

    id_contract = Column(Integer, primary_key=True)

    round_id_contract = Column(Integer, ForeignKey('round.id_round'), nullable=False)
    info_contract = Column(JSON, nullable=False)

    owner_id_contract = Column(Integer, ForeignKey('player.userid_player'), nullable=False)
    target_id_contract = Column(Integer, ForeignKey('player.userid_player'), nullable=False)
    is_completed_contract = Column(Boolean, default=False, nullable=False)
    is_active_contract = Column(Boolean, default=True, nullable=False)
    date_completed_contract = Column(DateTime, nullable=True)

    created_contract = Column(DateTime, default=func.now(), nullable=False)
    modified_contract = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, owner, target, round_, info={}):
        self.owner_id_contract = owner
        self.target_id_contract = target
        self.round_id_contract = round_

        new_info = {
            "api": {
                #"firstname": info["api"]["firstname"],
                #"lastname": info["api"]["lastname"],
                "firstname": "*"*len(info["api"]["firstname"]),
                "lastname": "*"*len(info["api"]["lastname"]),
                "age": "???",
                "height": "???",
                "gender": 0,
            },
            "survey": {
                "target": [],
            }
        }

        self.info_contract = new_info

class Round(Base):
    __tablename__ = "round"

    id_round = Column(Integer, primary_key=True)

    is_active_round = Column(Boolean, default=False, nullable=False)
    startdate_round = Column(DateTime, nullable=False)
    enddate_round = Column(DateTime, nullable=False)

    created_round = Column(DateTime, default=func.now(), nullable=False)
    modified_round = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, start, end):
        self.startdate_round = start
        self.enddate_round = end
