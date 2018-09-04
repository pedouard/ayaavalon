from .utils import reset_db
from ayaavalon.database import Player, add_game_stats, Game
from ayaavalon.stats import get_role_stats
import glob
import json
import os


def test_role_stats():
    session = reset_db()

    uids = range(100, 112)

    # adding users
    for userid in uids:
        player = Player(userid, {})
        session.add(player)

    files = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*.json'))
    assert len(files), "No game .json found."

    # adding games
    for file_ in files:
        d = json.loads(open(file_, 'r').read())
        v = -1
        game_record = Game(info=d, version=v)
        session.add(game_record)
        session.commit()
        print('added game record', d)

        add_game_stats(game_record.id_game, d, session)
        print('added stats record')

    # getting roles
    role_stats = get_role_stats(session)
    print(role_stats)
