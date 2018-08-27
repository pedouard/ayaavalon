# -*- coding: UTF-8 -*

import os
import json
import time
from flask import Flask, Response
from webargs import fields
from webargs.flaskparser import use_kwargs
from datetime import datetime

from lib import utils
from lib.db.database import Player, Game
from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions, json_response, WithingsException

import status
from www import app, session, auto, rollback_on_exception

@auto.doc()
@app.route("/player/get")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def player_get(userid, sessionid):
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })


@auto.doc()
@app.route("/player/create")
@nocache
@use_kwargs({
    'userid': fields.Int(required=True),
})
@handle_exceptions
@rollback_on_exception
def player_create(userid, sessionid):
    session.commit()
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })
