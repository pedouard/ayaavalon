# -*- coding: UTF-8 -*
import time
import random
import json
from datetime import datetime, timedelta

from withings.datascience.core import config
from withings.api import WithingsAPI
from lib.db.database import Player, Game
from www import status

"""
def format_contract(c, session):
    target = session.query(Player).filter_by(userid_player=c.target_id_contract).one()
    completed = time.mktime(c.date_completed_contract.timetuple()) if c.date_completed_contract is not None else None
    return {
        "contractid": c.id_contract,
        "ownerid": c.owner_id_contract,
        "targetid": c.target_id_contract,
        "target_playerid": target.id_player,
        "info": c.info_contract,
        "is_completed": c.is_completed_contract,
        "is_active": c.is_active_contract,
        "date_completed": completed,
        "modified": time.mktime(c.modified_contract.timetuple()),
        "created": time.mktime(c.created_contract.timetuple())
        }


def get_current_round(session):
    now = datetime.now()
    rounds = session.query(Round).filter_by(is_active_round=True).all()
    if len(rounds) == 0:
        return None

    return rounds[0]

def round_is_ongoing(session):
    round_ = get_current_round(session)
    if round_ is None:
        return False

    players = session.query(Player).filter_by(is_alive_player=True).all()
    return (len(players) > 1)
"""
