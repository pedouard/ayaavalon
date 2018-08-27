# -*- coding: UTF-8 -*

import os
import json
import time
from flask import Flask, Response
from webargs import fields
from webargs.flaskparser import use_kwargs
from datetime import datetime

from lib import utils, game
from lib.db.database import Player, Game
from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions, json_response, WithingsException

import status
from www import app, session, auto, rollback_on_exception

g = game.Game()

@auto.doc()
@app.route("/get_game")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def get_game(userid):
    # TODO
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })


@auto.doc()
@app.route("/join_game")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def join_game(userid):
    player = session.query(Player).filter_by(userid_player=userid).first()
    if player is None:
        raise WithingsException(*status.USER_NOT_FOUND)

    print g._get_by_userid(userid)
    if g._get_by_userid(userid):
        raise WithingsException(*status.ALREADY_IN_THE_GAME)

    if g.is_started:
        raise WithingsException(*status.GAME_IS_STARTED)

    if g.nplayers == 10:
        raise WithingsException(*status.GAME_IS_FULL)

    g.add_player(player)

    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@auto.doc()
@app.route("/start_game")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def start_game(userid):
    p = check_player(userid)

    if not p.is_host:
        raise WithingsException(*status.MUST_BE_HOST)

    if g.nplayers not in game.GAME_SETUPS:
        raise WithingsException(*status.NOT_ENOUGH_PLAYERS)

    g.start()

    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@auto.doc()
@app.route("/stop_game")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def stop_game(userid):
    # TODO
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@auto.doc()
@app.route("/reorder_players")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def reorder_players(userid):
    # TODO
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@auto.doc()
@app.route("/mission_start")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def start_mission(userid):
    # TODO
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@auto.doc()
@app.route("/vote")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def vote(userid):
    # TODO
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@auto.doc()
@app.route("/do_mission")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def do_mission(userid):
    # TODO
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })


@auto.doc()
@app.route("/kill_merlin")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
    # TODO
def kill_merlin(userid):
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })


def check_player(userid):
    player = session.query(Player).filter_by(userid_player=userid).first()
    if player is None:
        raise WithingsException(*status.USER_NOT_FOUND)

    p = g._get_by_userid(userid)
    if not p:
        raise WithingsException(*status.ALREADY_IN_THE_GAME)

    return p
