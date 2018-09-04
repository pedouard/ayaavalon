# -*- coding: UTF-8 -*

import json
from datetime import datetime, date

from flask import Response
from withings.datascience.core.flask_utils import nocache, \
    handle_exceptions

from ayaavalon.www import status
from ayaavalon.database import Game, GameStats

from ayaavalon.database import session
from ayaavalon.www import app
from ayaavalon.stats import get_role_stats


# TODO use this json_response everywhere
def default(o):
  if type(o) is date or type(o) is datetime:
    return o.isoformat()


def json_response(res):
    r = Response(json.dumps(res, default=default), mimetype='application/json')
    r.headers['Access-Control-Allow-Origin'] = '*'

    return r


def format_game(g_, stats=None):
    d = {
        "id": g_.id_game,
        "version": g_.version_game,
        "data": g_.info_game,
        "created": g_.created_game,
        "modified": g_.modified_game,
    }
    if stats is not None:
        d['stats'] = stats.__dict__
    return d


@app.route("/games")
@nocache
@handle_exceptions
def get_list_games():
    games = session.query(Game)
    # TODO paginate

    return json_response({
        'status': status.OK,
        'body': {
            'n_game': games.count(),
            'games': [format_game(g_) for g_ in games.all()],
        }
    })


@app.route("/games/<id>")
@nocache
@handle_exceptions
def get_game(id):
    game = session.query(Game).filter(Game.id_game == int(id)).one()
    game_stats = session.query(GameStats).filter(Game.id_game == int(id)).one_or_none()

    return json_response({
        'status': status.OK,
        'body': format_game(game, game_stats),
    })

@app.route("/stats/roles")
@nocache
@handle_exceptions
def get_stats_roles():
    return json_response({
        'status': status.OK,
        'body': get_role_stats(session),
    })

@app.route("/stats")
@nocache
@handle_exceptions
def get_stats():

    gs = session.query(GameStats)
    n_game = gs.count()
    n_good_wins = gs.filter(GameStats.good_wins).count()

    stats = {
        'n_game': n_game,
        'n_evil_wins': n_game - n_good_wins,
        'n_good_wins': n_good_wins,
        'r_evil_wins': (n_game - n_good_wins) / n_game,
        'r_good_wins': n_good_wins / n_game,
    }
    print('toot', stats)

    # ideas of badges / achievements

    # hidden merlin :
    # 1 point for voting for a known evil guy as merlin
    # 3 point for putting for a known evil guy as merlin
    # mean over game where the player is merlin

    # i'm not that guy :
    # most lady of the lake verified galahad

    return json_response({
        'status': status.OK,
        'body': stats,
    })
