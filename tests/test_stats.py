from .utils import reset_db
from ayaavalon.database import Player, add_game_stats, Game
from ayaavalon.stats import get_role_stats
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
        print('added game record', d)

        add_game_stats(game_record.id_game, d, session)
        print('added stats record')


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

