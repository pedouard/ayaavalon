# -*- coding: utf-8 -*
import sys
import os

import time
import datetime
from flask import Flask, Response
from webargs import fields
from webargs.flaskparser import use_kwargs

from lib import utils
from lib.db.database import Player, Contract
from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions, json_response, WithingsException

import status
from www import app, api, session, auto, rollback_on_exception, check_groupid

reload(sys)
sys.setdefaultencoding('utf-8')

@auto.doc()
@app.route("/contract/create")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'userid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def contract_create(userid, sessionid):
    """ Create a new contract for the given player
    """
    st, new_contract = utils.proxy_contract_create(userid, session)

    if st != status.OK:
        raise WithingsException(*st)

    return json_response({'status': status.OK, 'body': utils.format_contract(new_contract, session)})

@auto.doc()
@app.route("/contract/complete")
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'contractid': fields.Int(required=True),
    'sessionid': fields.Str(required=True),
    'forreal': fields.Boolean(required=False, missing=True),
})
@handle_exceptions
@check_groupid
@rollback_on_exception
def contract_complete(contractid, sessionid, forreal):
    """ Mark a contract as completed
    """
    contracts = session.query(Contract).filter_by(id_contract=contractid).all()
    if len(contracts) == 0:
        raise WithingsException(*status.CONTRACT_NOT_FOUND)

    contract = contracts[0]
    if contract.is_completed_contract:
        raise WithingsException(*status.CONTRACT_ALREADY_COMPLETED)

    if not contract.is_active_contract:
        raise WithingsException(*status.CONTRACT_INACTIVE)

    target_players = session.query(Player).filter_by(userid_player=contract.target_id_contract).all()
    if len(target_players) == 0:
        raise WithingsException(*status.USER_NOT_FOUND)

    owner_players = session.query(Player).filter_by(userid_player=contract.owner_id_contract).all()
    if len(owner_players) == 0:
        raise WithingsException(*status.USER_NOT_FOUND)

    target_player, owner_player = target_players[0], owner_players[0]

    if not owner_player.is_alive_player:
        raise WithingsException(*status.CONTRACT_OWNER_IS_DEAD)

    if target_player.is_alive_player and forreal:
        # Send notification
        try:
            title = "%s %s vous a tué%s!" % (
                owner_player.info_player["api"]["firstname"],
                owner_player.info_player["api"]["lastname"],
                "" if target_player.info_player["api"]["gender"] == 0 else "e"
                )
            message = "Vous êtes éliminé%s pour la journée, vous avez marqué %d point%s aujourd'hui." % (
                "" if target_player.info_player["api"]["gender"] == 0 else "e",
                target_player.round_points_player,
                "" if owner_player.round_points_player == 0 else "s"
                )

            data_message = {"notif_reason": 1} # Death

            utils.send_notif(target_player.token_player, target_player.is_ios_player, title, message,
                             data_message=data_message)

        except Exception, e:
            pass
    if forreal:
        owner_player.total_points_player += 1
        owner_player.round_points_player += 1

    target_player.is_alive_player = False

    contract.is_completed_contract = True
    contract.is_active_contract = False
    contract.date_completed_contract = datetime.datetime.now()
    contract.info_contract = target_player.info_player

    # Deactive all of the target's contracts
    target_contracts = session.query(Contract).filter_by(owner_id_contract=target_player.userid_player).all()
    for c in target_contracts:
        c.is_active_contract = False

    session.commit()

    __dir__ = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(__dir__, "kills"), "a") as f:
        f.write("%s - %s %s killed %s %s\n" % (
            datetime.datetime.now(),
            owner_player.info_player["api"]["firstname"],
            owner_player.info_player["api"]["lastname"],
            target_player.info_player["api"]["firstname"],
            target_player.info_player["api"]["lastname"]
        ))

    utils.send_refresh_all_notif(session)
    return json_response({'status': status.OK, 'body': utils.format_contract(contract, session)})
