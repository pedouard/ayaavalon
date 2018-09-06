from .utils import reset_db
from ayaavalon.database import Player, add_game_stats, Game
from ayaavalon.stats import get_role_stats, get_connection_stats
import glob
import json
import os


def add_users(uids, session):
    for userid in uids:
        player = Player(userid, {})
        session.add(player)


def load_games(option, session):
    if option == 'all':
        files = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*.json'))
        assert len(files), "No game .json found."
    elif type(option) == list:
        files = [os.path.join(os.path.dirname(__file__), 'data', 'game_{:03}.json'.format(x)) for x in option]
    else:
        raise Exception()

    for file_ in files:
        d = json.loads(open(file_, 'r').read())
        v = -1
        game_record = Game(info=d, version=v)
        session.add(game_record)
        session.commit()

        add_game_stats(game_record.id_game, d, session)


def test_role_stats():
    session = reset_db()

    add_users(range(100, 111), session)
    load_games([0, 1], session)

    # getting roles
    role_stats = get_role_stats(session)
    expected = {
        'role_Merlin': [(101, 1), (108, 1)],
        'role_Percival': [(103, 1), (107, 1)],
        'role_Galahad': [],
        'role_Assassin': [(104, 1), (105, 1)],
        'role_Mordred': [(100, 1), (104, 1)],
        'role_Morgana': [(109, 2)],
        'role_Good guy': [(106, 2), (100, 1), (101, 1), (102, 1), (103, 1),  (107, 1), (108, 1)],
        'role_Oberon': [(102, 1), (105, 1)],
        'role_Bad Guy': [],
    }
    assert role_stats == expected


def test_connection_stats():
    session = reset_db()

    add_users(range(100, 111), session)
    load_games([0, ], session)

    connection_stats = get_connection_stats(session)
    expected = {
        "voted_for": [(100, 100, 4), (100, 101, 4), (100, 102, 4), (100, 103, 3), (100, 104, 2), (101, 100, 4), (101, 101, 4), (101, 102, 4), (101, 103, 3), (101, 104, 2), (102, 100, 4), (102, 101, 4), (102, 102, 4), (102, 103, 3), (102, 104, 2), (103, 100, 4), (103, 101, 4), (103, 102, 4), (103, 103, 3), (103, 104, 2), (104, 100, 4), (104, 101, 4), (104, 102, 4), (104, 103, 3), (104, 104, 2), (105, 100, 4), (105, 101, 4), (105, 102, 4), (105, 103, 3), (105, 104, 2), (106, 100, 4), (106, 101, 4), (106, 102, 4), (106, 103, 3), (106, 104, 2), (107, 100, 4), (107, 101, 4), (107, 102, 4), (107, 103, 3), (107, 104, 2), (108, 100, 4), (108, 101, 4), (108, 102, 4), (108, 103, 3), (108, 104, 2), (109, 100, 4), (109, 101, 4), (109, 102, 4), (109, 103, 3), (109, 104, 2)],
        "voted_against": [(100, 100, 4), (100, 101, 4), (100, 102, 4), (100, 103, 4), (101, 100, 4), (101, 101, 4), (101, 102, 4), (101, 103, 4), (102, 100, 4), (102, 101, 4), (102, 102, 4), (102, 103, 4), (103, 100, 4), (103, 101, 4), (103, 102, 4), (103, 103, 4), (104, 100, 4), (104, 101, 4), (104, 102, 4), (104, 103, 4), (105, 100, 4), (105, 101, 4), (105, 102, 4), (105, 103, 4), (106, 100, 4), (106, 101, 4), (106, 102, 4), (106, 103, 4), (107, 100, 4), (107, 101, 4), (107, 102, 4), (107, 103, 4), (108, 100, 4), (108, 101, 4), (108, 102, 4), (108, 103, 4), (109, 100, 4), (109, 101, 4), (109, 102, 4), (109, 103, 4)]
    }
    assert connection_stats == expected
