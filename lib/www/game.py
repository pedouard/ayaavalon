# -*- coding: UTF-8 -*

import os
import json
import time
from flask import Flask, Response
from webargs import fields
from webargs.flaskparser import use_kwargs
from datetime import datetime

from lib import utils
from lib.db.database import Round
from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions, json_response, WithingsException

import status
from www import app, api, session, auto, rollback_on_exception,check_groupid

@auto.doc()
@app.route("/game/get")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'sessionid': fields.Str(required=True)
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def game_get(sessionid):
    rounds = session.query(Round).all()
    rounds = sorted(rounds, key=lambda r: r.startdate_round)

    body = {
        "rounds": [format_round(r) for r in rounds],
        "startdate": 0,
        "enddate": 0,
        "has_active_round": False,
        "active_round_idx": 0,
        "has_started": False,
        "has_ended": False,
        "n_rounds": len(rounds)
    }

    for i, r in enumerate(body["rounds"]):
        if r["is_active"]:
            body["has_active_round"] = True
            body["active_round_idx"] = i

        if r["startdate"] < body["startdate"] or body["enddate"] == 0:
            body["startdate"] = r["startdate"]

        if r["enddate"] > body["enddate"]:
            body["enddate"] = r["enddate"]

    now = time.mktime(datetime.now().timetuple())
    if body["startdate"] < now and body["startdate"] != 0:
        body["has_started"] = True

    if body["enddate"] < now and body["enddate"] != 0:
        body["has_ended"] = True

    return json_response({
        'status': status.OK,
        'body': body
        })

def format_round(r):
    return {
        "id": r.id_round,
        "is_active": r.is_active_round,
        "startdate": time.mktime(r.startdate_round.timetuple()),
        "enddate": time.mktime(r.enddate_round.timetuple()),
        "created": time.mktime(r.created_round.timetuple()),
        "modified": time.mktime(r.modified_round.timetuple())
        }

