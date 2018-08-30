# -*- coding: UTF-8 -*

import json

from webargs import fields
from webargs.flaskparser import use_kwargs
from withings.datascience.core.flask_utils import nocache, handle_exceptions, json_response, \
    WithingsException

import lib.www.status as status
from lib import utils
from lib.db.database import Player
from lib.www.www import app, session, auto, rollback_on_exception


@auto.doc()
@app.route("/player_get")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def player_get(userid):
    player = session.query(Player).filter_by(userid_player=userid).first()

    if player is None:
        raise WithingsException(*status.USER_NOT_FOUND)

    return json_response({
        'status': status.OK,
        'body': utils.format_player(player)
        })


@auto.doc()
@app.route("/player_create")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
    'info': fields.Str(required=True),
})
@handle_exceptions
@rollback_on_exception
def player_create(userid, info):
    player = session.query(Player).filter_by(userid_player=userid).first()

    if player is not None:
        raise WithingsException(*status.USER_ALREADY_EXISTS)


    info = json.loads(info)
    player = Player(userid, info)
    session.add(player)

    session.commit()
    return json_response({
        'status': status.OK,
        'body': {
            "id": player.id_player
            }
        })
