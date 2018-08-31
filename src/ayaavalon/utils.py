# -*- coding: UTF-8 -*
import time

from ayaavalon.database import Player, Game
from ayaavalon.www import app
from ayaavalon import config


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


class AppClient(object):
    """
        Usual class for unittesting.
        Will tests all cases possible for all the routes.
    """
    app.config['TESTING'] = True

    def __init__(self):
        self.app = app.test_client()
        # self.app.set_cookie('localhost', config.get('ayaavalon', 'session_cookie_name'), bytes([12]))


ayaavalon_app = AppClient()

