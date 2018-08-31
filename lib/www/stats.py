# -*- coding: UTF-8 -*

import json
from datetime import datetime, date

from flask import Response
from withings.datascience.core.flask_utils import nocache, \
    handle_exceptions

import lib.www.status as status
from lib.db.database import Game, GameStats
from lib.www.www import app, session


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


@app.route("/stats/games")
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


@app.route("/stats/games/<id>")
@nocache
@handle_exceptions
def get_game(id):
    game = session.query(Game).filter(Game.id_game == int(id)).one()
    game_stats = session.query(GameStats).filter(Game.id_game == int(id)).one_or_none()

    return json_response({
        'status': status.OK,
        'body': format_game(game, game_stats),
    })
