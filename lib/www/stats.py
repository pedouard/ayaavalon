# -*- coding: UTF-8 -*

import os
import json
import time
from flask import Flask, Response
from webargs import fields
from webargs.flaskparser import use_kwargs
from datetime import datetime, date

from lib import utils, game
from lib.db.database import Game
from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions, WithingsException

import lib.www.status as status
from lib.www.www import app, session, auto, rollback_on_exception
from lib.www.game import format_game


# TODO use this json_response everywhere
def default(o):
  if type(o) is date or type(o) is datetime:
    return o.isoformat()


def json_response(res):
    r = Response(json.dumps(res, default=default), mimetype='application/json')
    r.headers['Access-Control-Allow-Origin'] = '*'

    return r


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

    return json_response({
        'status': status.OK,
        'body': format_game(game),
    })
