# -*- coding: UTF-8 -*
import time

from lib.db.database import Player, Game


def format_player(player):
    return {
        "id": player.id_player,
        "userid": player.userid_player,
        "info": player.info_player,
        "modified": time.mktime(player.modified_player.timetuple()),
        "created": time.mktime(player.created_player.timetuple())
    }

def truncate_all_tables(session):
    n = session.query(Game).delete()
    print('deleted {} game records'.format(n))
    n = session.query(Player).delete()
    print('deleted {} player records'.format(n))
    session.commit()
