# -*- coding: UTF-8 -*

import json

from webargs import fields
from webargs.flaskparser import use_kwargs
from withings.datascience.core.flask_utils import nocache, \
    handle_exceptions, json_response, WithingsException

import lib.www.status as status
from lib import game
from lib.db.database import Player
from lib.www.www import app, session

g = game.Game(session)

@app.route("/get_game_state")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
def get_game_state(userid):
    player = session.query(Player).filter_by(userid_player=userid).first()
    if player is None:
        raise WithingsException(*status.USER_NOT_FOUND)

    p = g._get_by_id_player(player.id_player)
    return json_response({
        'status': status.OK,
        'body': g.dump_state(p)
        })


@app.route("/join_game")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
def join_game(userid):
    player = session.query(Player).filter_by(userid_player=userid).first()
    if player is None:
        raise WithingsException(*status.USER_NOT_FOUND)

    g.add_player(player)

    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })


@app.route("/start_game")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
def start_game(userid):
    id_player = session.query(Player).filter_by(userid_player=userid).first().id_player
    p = check_player(id_player)
    g.start(p)
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })


@app.route("/abort_game")
@nocache
@use_kwargs({})
@handle_exceptions
def abort_game():
    global g
    g = game.Game(session)
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })


# @app.route("/reorder_players")
# @nocache
# @use_kwargs({
#     'userid': fields.Int(required=True),
# })
# @handle_exceptions
# def reorder_players(userid):
#     # TODO
#     return json_response({
#         'status': status.OK,
#         'body': "Ok!"
#         })


@app.route("/propose_mission")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
    'members': fields.String(required=True),
    'lady': fields.Int(required=False),
})
@handle_exceptions
def propose_mission(userid, members, lady=0):
    id_player = session.query(Player).filter_by(userid_player=userid).first().id_player
    p = check_player(id_player)
    members = json.loads(members)
    g.propose_mission(p, members, lady)

    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@app.route("/vote")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
    'v': fields.Boolean(required=True),
})
@handle_exceptions
def vote(userid, v):
    id_player = session.query(Player).filter_by(userid_player=userid).first().id_player
    p = check_player(id_player)
    g.vote(p, v)

    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@app.route("/do_mission")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
    'v': fields.Boolean(required=True),
})
@handle_exceptions
def do_mission(userid, v):
    id_player = session.query(Player).filter_by(userid_player=userid).first().id_player
    p = check_player(id_player)
    g.do_mission(p, v)

    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })


@app.route("/kill_merlin")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
    'target': fields.Int(required=True),
})
@handle_exceptions
# TODO can kill merlin even if evil won
# TODO cannot kill yourself or a an evil guy
def kill_merlin(userid, target):
    id_player = session.query(Player).filter_by(userid_player=userid).first().id_player
    p = check_player(id_player)
    g.assassinate(p, target)

    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@app.route("/use_lady")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
    'target': fields.Int(required=True),
})
@handle_exceptions
    # TODO
def use_lady(userid, target):
    id_player = session.query(Player).filter_by(userid_player=userid).first().id_player
    p = check_player(id_player)

    return json_response({
        'status': status.OK,
        'body': g.use_lady(p, target)
        })


@app.route("/dump_database")
@nocache
@use_kwargs({})
@handle_exceptions
def dump_database():
    raise DeprecationWarning('Use /stats/games/<id> instead')


#TODO refacto : get id_player from session_id, and check_player in a decorator
def check_player(id_player):
    player = session.query(Player).filter_by(id_player=id_player).first()
    if player is None:
        raise WithingsException(*status.USER_NOT_FOUND)

    p = g._get_by_id_player(id_player)
    if not p:
        raise WithingsException(*status.NOT_IN_THE_GAME)

    return p
