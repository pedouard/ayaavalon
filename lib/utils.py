# -*- coding: UTF-8 -*
import time
import random
import json
from pyfcm import FCMNotification
from datetime import datetime, timedelta

from withings.datascience.core import config
from withings.api import WithingsAPI
from lib.db.database import Round, Contract, Player
from www import status

def format_contract(c, session):
    target = session.query(Player).filter_by(userid_player=c.target_id_contract).one()
    completed = time.mktime(c.date_completed_contract.timetuple()) if c.date_completed_contract is not None else None
    return {
        "contractid": c.id_contract,
        "ownerid": c.owner_id_contract,
        "targetid": c.target_id_contract,
        "target_playerid": target.id_player,
        "info": c.info_contract,
        "is_completed": c.is_completed_contract,
        "is_active": c.is_active_contract,
        "date_completed": completed,
        "modified": time.mktime(c.modified_contract.timetuple()),
        "created": time.mktime(c.created_contract.timetuple())
        }


def get_current_round(session):
    now = datetime.now()
    rounds = session.query(Round).filter_by(is_active_round=True).all()
    if len(rounds) == 0:
        return None

    return rounds[0]

def round_is_ongoing(session):
    round_ = get_current_round(session)
    if round_ is None:
        return False

    players = session.query(Player).filter_by(is_alive_player=True).all()
    return (len(players) > 1)


def send_notif(token, is_ios, title=None, message=None, data_message={}):
    # https://pypi.python.org/pypi/pyfcm/
    push_service = FCMNotification(api_key=config.get('ayaa', 'fb_private'))

    extra_kwargs = {'mutable_content': True}
    data_message["source"] = "ayaa"

    if title is None:
        push_service.notify_single_device(registration_id=token, data_message=data_message,
                                          content_available=True, extra_kwargs=extra_kwargs)
        return


    title = "Ayaa! - " + title
    if is_ios:
        push_service.notify_single_device(registration_id=token, data_message=data_message,
                                          content_available=True, extra_kwargs=extra_kwargs)

        push_service.notify_single_device(registration_id=token, data_message=data_message,
                                          message_title=title, message_body=message,
                                          content_available=True, extra_kwargs=extra_kwargs)
    else: # Android
        data_message["title"] = title
        data_message["message"] = message
        push_service.notify_single_device(registration_id=token, data_message=data_message,
                                          content_available=True, extra_kwargs=extra_kwargs)

def send_refresh_all_notif(session):
    broadcast_notif(session, data_message={"notif_reason": 2})

def broadcast_notif(session, title=None, message=None, data_message={}):
    players = session.query(Player).all()
    tokens_ios = [p.token_player for p in players if p.is_ios_player]
    tokens_android = [p.token_player for p in players if not p.is_ios_player]

    push_service = FCMNotification(api_key=config.get('ayaa', 'fb_private'))
    data_message["source"] = "ayaa"
    extra_kwargs = {'mutable_content': True}

    if title is None:
        push_service.notify_multiple_devices(registration_ids=tokens_ios + tokens_android, data_message=data_message,
                                             content_available=True, extra_kwargs=extra_kwargs,
                                             low_priority=False)
        return

    title = "Ayaa! - " + title
    try:
        # ios
        push_service.notify_multiple_devices(registration_ids=tokens_ios, data_message=data_message,
                                             message_title=title, message_body=message,
                                             content_available=True, extra_kwargs=extra_kwargs,
                                             low_priority=False)

        push_service.notify_multiple_devices(registration_ids=tokens_ios, data_message=data_message,
                                             content_available=True, extra_kwargs=extra_kwargs,
                                             low_priority=False)

        # android
        data_message["title"] = "Ayaa! - " + title
        data_message["message"] = message
        push_service.notify_multiple_devices(registration_ids=tokens_android, data_message=data_message,
                                             content_available=True, extra_kwargs=extra_kwargs,
                                             low_priority=False)
    except Exception, e:
        print
        print
        print e
        print
        print

def revert_all_deploy_groups(session):
    players = session.query(Player).all()
    api = WithingsAPI(auto_logout=False)
    api.login("paul.edouard@withings.com", "qwertyqwerty")
    for p in players:
        api.call("v2/firmware", "deviceupdate", mac_addresses=json.dumps([p.mac_player]),
            deploygrp=p.previous_deploy_grp_player, model=55)


def truncate_all_tables(session):
    revert_all_deploy_groups(session)

    session.query(Contract).delete()
    session.query(Round).delete()
    session.query(Player).delete()
    session.commit()

def add_round(session, date, tdstart=None, tdend=None):
    date = date.replace(hour=0, minute=0, second=0)
    tdstart = tdstart or timedelta(hours=1, minutes=0)
    tdend = tdend or timedelta(hours=23, minutes=30)

    startdate = date + tdstart
    enddate = date + tdend

    existing_rounds = session.query(Round).all()
    for r in existing_rounds:
        if r.startdate_round <= startdate <= r.enddate_round or r.startdate_round <= enddate <= r.enddate_round \
                or startdate <= r.startdate_round <= enddate or startdate <= r.enddate_round <= enddate:
            raise Exception("Cant create round from %s to %s because of another round between %s and %s" % (
                startdate, enddate, r.startdate_round, r.enddate_round))

    r = Round(start=startdate, end=enddate)
    session.add(r)
    session.commit()


def check_all_rounds(session):
    now = datetime.now()
    rounds = session.query(Round).all()

    for r in rounds:
        if r.startdate_round <= now <= r.enddate_round and not r.is_active_round:
            start_round(r, session)

        if r.enddate_round < now and r.is_active_round:
            end_round(r, session)

def start_round(r, session):
    r.is_active_round = True

    players = session.query(Player).all()
    for p in players:
        p.is_alive_player = True
        p.is_active_player = True
        p.round_points_player = 0

    if len(players) > 1:
        for p in players:
            proxy_contract_create(p.userid_player, session)

    session.commit()
    broadcast_notif(session, title="La partie Ayaa est lancée !",
                    message="Ouvre ton application pour découvrir ta première cible. Si tu ne devine pas qui c'est, attends, des indices te seront donnés !",
                    data_message={"notif_reason": 3})

def end_round(r, session):
    r.is_active_round = False

    players = session.query(Player).all()
    for p in players:
        p.is_active_player = False
        p.is_alive_player = False
        p.round_points_player = 0

    contracts = session.query(Contract).all()
    for c in contracts:
        c.is_active_contract = False

    session.commit()
    send_refresh_all_notif(session)

def proxy_contract_create(userid, session):
    round_ = get_current_round(session)
    if round_ is None:
        return status.NO_CURRENT_ACTIVE_ROUND, None

    contracts = session.query(Contract).filter_by(owner_id_contract=userid).filter_by(is_active_contract=True).all()
    if len(contracts) != 0:
        return status.ACTIVE_CONTRACT_ALREADY_EXISTS, None

    players = session.query(Player).filter_by(userid_player=userid).filter_by(is_alive_player=True).all()
    if len(players) == 0 or not players[0].is_active_player:
        return status.USER_ID_DEAD, None

    players = session.query(Player).filter_by(is_active_player=True).filter_by(is_alive_player=True).filter(Player.userid_player != userid).all()
    if len(players) == 0:
        return status.NOT_ENOUGH_PLAYERS, None

    target = players[random.randrange(len(players))]
    # + Utils get initial info
    new_contract = Contract(owner=userid, target=target.userid_player, round_=round_.id_round, info=target.info_player)

    tmp = unlock_clues(new_contract.info_contract, target.info_player)
    new_contract.info_contract["api"] = tmp["api"]
    new_contract.info_contract["survey"] = tmp["survey"]

    session.add(new_contract)
    session.commit()

    return status.OK, new_contract

def unlock_clues(info_c, info_p):
    firstname = list(info_c["api"]["firstname"])
    lastname = list(info_c["api"]["lastname"])

    for i in range(100):
        rnd = random.randrange(4)
        if rnd == 0: # Firstname
            rnd = random.randrange(len(firstname))
            if firstname[rnd] == "*":
                firstname[rnd] = info_p["api"]["firstname"][rnd]
                info_c["api"]["firstname"] = "".join(firstname)
                break
            else:
                continue

        elif rnd == 1: # Lastname
            rnd = random.randrange(len(lastname))
            if lastname[rnd] == "*":
                lastname[rnd] = info_p["api"]["lastname"][rnd]
                info_c["api"]["lastname"] = "".join(lastname)
                break
            else:
                continue

        elif rnd == 2: # Age
            if info_c["api"]["age"] == "???":
                info_c["api"]["age"] = info_p["api"]["age"]
                break
            else:
                continue

        elif rnd == 3: # height
            if info_c["api"]["height"] == "???":
                info_c["api"]["height"] = info_p["api"]["height"]
                break
            else:
                continue


    clues = info_p["survey"]["target"]
    unlocked_clues = info_c["survey"]["target"]
    for i in range(100):
        if len(clues) == 0 or len(unlocked_clues) == len(clues):
            break

        rnd = random.randrange(len(clues))
        if clues[rnd] not in unlocked_clues:
            info_c["survey"]["target"].append(clues[rnd])
            break

    return info_c
