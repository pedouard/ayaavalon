# -*- coding: UTF-8 -*

import os
import json
import time
from flask import Flask, Response
from webargs import fields
from webargs.flaskparser import use_kwargs
from datetime import datetime

from lib import utils
from lib.db.database import Player, Contract
from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions, json_response, WithingsException

import status
from www import app, api, session, auto, rollback_on_exception, check_groupid

AYAA_DEPLOY_GRP = 10064

__dir__ = os.path.dirname(os.path.realpath(__file__))
whitelist = open(os.path.join(__dir__, "userid_whitelist")).read().split("\n")
whitelist = map(int, whitelist[:-1])

@auto.doc()
@app.route("/player/is_whitelisted")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'userid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def player_is_whitelisted(userid, sessionid):
    #if userid not in whitelist:
    #    raise WithingsException(*status.USER_NOT_AUTHORIZED)

    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@auto.doc()
@app.route("/player/revive")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'userid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def player_revive(userid, sessionid):

    players = session.query(Player).filter_by(userid_player=userid).all()
    if len(players) == 0:
        raise WithingsException(*status.USER_NOT_FOUND)

    p = players[0]
    p.is_alive_player = True
    p.is_active_player = True
    session.commit()

    utils.send_refresh_all_notif(session)
    return json_response({
        'status': status.OK,
        'body': "Ok!"
        })

@auto.doc()
@app.route("/player/create")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'userid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
    'token': fields.Str(required=True),
    'deviceid': fields.Int(required=True),
    'info': fields.Str(required=False, missing="{}")
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def player_create(userid, sessionid, info, token, deviceid):
    """ Creates a new player, fetches info from Withings API
    """
    duplicate = session.query(Player).filter_by(userid_player=userid).all()
    if len(duplicate) != 0:
        raise WithingsException(*status.USER_ALREADY_EXISTS)

    #if userid not in whitelist:
    #    raise WithingsException(*status.USER_NOT_AUTHORIZED)

    api.set_session(sessionid)
    info = json.loads(info)

    #### Call Withings API to get device data ####
    device_res = api.call("v2/device", "get", deviceid=deviceid)
    if device_res["status"] != 0:
        raise WithingsException(*status.UNEXPECTED_API_ANSWER)

    model = device_res["body"]["device"]["model"]
    if model != 55:
        raise WithingsException(*status.WRONG_DEVICE_MODEL)

    mac_address = device_res["body"]["device"]["mac_address"]
    id_deploy_grp = device_res["body"]["device"]["id_deploy_grp"]

    # save deploy grp
    __dir__ = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(__dir__, "deploy_grp_list"), "a") as f:
        f.write("%s,%d\n" % (mac_address, id_deploy_grp))

    #### Call Withings API to get additional data ####
    user_res = api.call("v2/user", "get", userid=userid, enrich="t")
    if user_res["status"] != 0:
        raise WithingsException(*status.UNEXPECTED_API_ANSWER)
    user_res = user_res["body"]["user"]

    #### Get pictures urls ####
    user_v1_res = api.call("user", "getbyuserid", userid=userid, enrich="t")
    if user_v1_res["status"] != 0:
        raise WithingsException(*status.UNEXPECTED_API_ANSWER)

    p4 = user_v1_res["body"]["users"][0]["p4"]
    base_url = "https://p4.withings.com/"
    url_64 = base_url + p4["64x64"] if "64x64" in p4 else None
    url_128 = base_url + p4["128x128"] if "128x128" in p4 else None
    url_256 = base_url + p4["256x256"] if "256x256" in p4 else None

    height_res = api.call("measure", "getmeas", userid=userid, meastype=4)
    if height_res["status"] != 0 or len(height_res["body"]["measuregrps"]) == 0:
        raise WithingsException(*status.UNEXPECTED_API_ANSWER)

    height_res = height_res["body"]["measuregrps"][0]["measures"][0]

    account_res = api.call("v2/account", "get")
    if account_res["status"] != 0:
        raise WithingsException(*status.UNEXPECTED_API_ANSWER)

    account_res = account_res["body"]["account"]
    ##################################################

    # Generate info JSON
    new_info = {
        "api": {
            "firstname": user_res["firstname"],
            "lastname": user_res["lastname"],
            "age": str(int((time.time() - user_res["birthdate"]) / (3600*24*365))),
            "gender": user_res["gender"],
            #"shortname": user_res["shortname"],
            "height": str(height_res["value"] * 10.0**height_res["unit"]),
            #"created": account_res["created"]
            },
        "survey": info
    }

    is_ongoing = utils.round_is_ongoing(session)

    # Add player to db
    new_player = Player(userid, new_info, token, deviceid, mac_address, id_deploy_grp,
                        url_64, url_128, url_256, is_active=is_ongoing,
                        is_alive=is_ongoing)

    session.add(new_player)
    session.commit()

    api.login("paul.edouard@withings.com", "qwertyqwerty")
    api.call("v2/firmware", "deviceupdate", mac_addresses=json.dumps([mac_address]),
        deploygrp=AYAA_DEPLOY_GRP, model=model)

    utils.send_refresh_all_notif(session)

    return json_response({
        'status': status.OK,
        'body': player_get_proxy(userid, p=new_player)
        }) # Return the created user

@auto.doc()
@app.route("/player/set_token")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'userid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
    'token': fields.Str(required=True),
    'is_ios': fields.Boolean(required=False, missing=False),
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def player_set_token(userid, sessionid, token, is_ios):
    players = session.query(Player).filter_by(userid_player=userid).all()
    if len(players) == 0:
        raise WithingsException(*status.USER_NOT_FOUND)

    p = players[0]
    p.token_player = token
    p.is_ios_player = is_ios
    session.commit()

    return json_response({
        'status': status.OK,
        'body': "Token successfuly updated"
        })


@auto.doc()
@app.route("/player/get")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'userid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def player_get(userid, sessionid):
    return json_response({
        'status': status.OK,
        'body': player_get_proxy(userid)
        })

@auto.doc()
@app.route("/player/send_notif")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'userid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
    'title': fields.Str(required=True),
    'message': fields.Str(required=True),
    'data': fields.Str(required=False, missing="{}")
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def player_send_notif(userid, sessionid, title, message, data):
    players = session.query(Player).filter_by(userid_player=userid).all()
    if len(players) == 0:
        raise WithingsException(*status.USER_NOT_FOUND)

    data = json.loads(data)
    if "notif_reason" not in data:
        data["notif_reason"] = 0 # Custom message

    p = players[0]
    utils.send_notif(p.token_player, p.is_ios_player, title, message, data_message=data)

    __dir__ = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(__dir__, "notifs"), "a") as f:
        f.write("%s - To %s %s : %s\n" % (
            datetime.now(),
            p.info_player["api"]["firstname"],
            p.info_player["api"]["lastname"],
            message
        ))

    return json_response({
        'status': status.OK,
        'body': {}
        })

@auto.doc()
@app.route("/player/get_all")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'sessionid': fields.Str(required=True)
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def player_get_all(sessionid):
    players = session.query(Player).all()
    return json_response({
        'status': status.OK,
        'body': [player_get_proxy(p.userid_player, p=p) for p in players]
        })

@auto.doc()
@app.route("/player/delete")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'userid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def player_delete(userid, sessionid):

    players = session.query(Player).filter_by(userid_player=userid).all()
    if len(players) == 0:
        raise WithingsException(*status.USER_NOT_FOUND)

    p = players[0]
    target_deploy_grp = p.previous_deploy_grp_player
    mac_address = p.mac_player

    api.login("paul.edouard@withings.com", "qwertyqwerty")
    api.call("v2/firmware", "deviceupdate", mac_addresses=json.dumps([mac_address]),
        deploygrp=target_deploy_grp, model=55)

    owned_contracts = session.query(Contract).filter_by(owner_id_contract=userid).all()
    targeted_contracts = session.query(Contract).filter_by(target_id_contract=userid).all()

    for c in owned_contracts:
        session.delete(c)

    for c in targeted_contracts:
        session.delete(c)

    session.commit()
    session.delete(p)
    session.commit()

    return json_response({'status': status.OK, 'body': {}})

def player_get_proxy(userid, p=None):
    """ Get the player data for a given userid
    """
    if p is None:
        players = session.query(Player).filter_by(userid_player=userid).all()
        if len(players) == 0:
            raise WithingsException(*status.USER_NOT_FOUND)

        p = players[0]

    other_players = session.query(Player).filter_by(is_active_player=True).filter_by(is_alive_player=True).filter(Player.userid_player != userid).all()
    player_has_won_round = p.is_alive_player and len(other_players) == 0

    contracts = session.query(Contract).filter_by(owner_id_contract=userid).all()
    contracts = sorted(contracts, key=lambda c: c.created_contract, reverse=True)

    return {
            "playerid": p.id_player,
            "userid": p.userid_player,
            "info": p.info_player,
            "is_active": p.is_active_player,
            "is_alive": p.is_alive_player,
            "is_ios": p.is_ios_player,
            "total_points": p.total_points_player,
            "round_points": p.round_points_player,
            "token": p.token_player,
            "player_has_won_round": player_has_won_round,

            "deviceid": p.deviceid_player,
            "mac": p.mac_player,
            "previous_deploy_grp": p.previous_deploy_grp_player,

            "url_64": p.url_64_player,
            "url_128": p.url_128_player,
            "url_256": p.url_256_player,
            "modified": time.mktime(p.modified_player.timetuple()),
            "created": time.mktime(p.created_player.timetuple()),
            "contracts": [utils.format_contract(c, session) for c in contracts]
            }
