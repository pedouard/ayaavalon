#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ayaavalon import utils, game
from ayaavalon.utils import ayaavalon_app
from ayaavalon.www.status import *

import requests
import json
import sys

from datetime import datetime

from .utils import reset_db

now = datetime.now()



def call(route, **kwargs):

    print("Calling:", route)
    kwargs = {k:str(v) for k,v in kwargs.items()}
    print("args", kwargs)
    # r = requests.get("http://0.0.0.0:6444" + route, params=kwargs)
    r = ayaavalon_app.app.get(route, data=kwargs)
    assert r.status_code == 200

    try:
        res = json.loads(r.get_data().decode(sys.getdefaultencoding()))
    except Exception:
        raise Exception("Failed to json decode:\n%s\n" % r.get_data())

    if res["status"] == 0:
        return res["status"], res["body"]
    else:
        return res["status"], res["error"]


def check_status(status, body, target):
    assert status == target, "%d != %d - %s" % (status, target, body)
    print("Ok")


def check_equal(value, target):
    assert value == target, "%s != %s" % (value, target)
    print("Ok")


def test_play_one_game():
    session = reset_db()

    status, body = call("/abort_game")
    check_status(status, body, 0)

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, USER_NOT_FOUND[0])

    print("Create good user")
    for i in range(11):
        status, body = call("/player_create", userid=100 + i, info="{}")
        check_status(status, body, 0)

    status, body = call("/player_create", userid=100, info="{}")
    check_status(status, body, USER_ALREADY_EXISTS[0])

    print("Get good user")
    for i in range(11):
        status, body = call("/player_get", userid=100 + i)
        check_status(status, body, 0)
        check_equal(body["userid"], 100+i)
        check_equal(body["info"], {})

    status, body = call("/player_get", userid=200)
    check_status(status, body, USER_NOT_FOUND[0])

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["nplayers"], 0)
    check_equal(body["state"], game.STATE_EMPTY)

    print("Add players")
    for i in range(10):
        status, body = call("/join_game", userid=100 + i)
        check_status(status, body, 0)

    status, body = call("/join_game", userid=110)
    check_status(status, body, GAME_IS_FULL[0])

    status, body = call("/join_game", userid=100)
    check_status(status, body, ALREADY_IN_THE_GAME[0])

    status, body = call("/propose_mission", userid=100, members=[0, 1, 2])
    check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["nplayers"], 10)
    check_equal(body["players"][0]["is_host"], True)
    check_equal(body["state"], game.STATE_NOT_STARTED)

    print("Starting game")
    status, body = call("/start_game", userid=101)
    check_status(status, body, MUST_BE_HOST[0])

    status, body = call("/start_game", userid=100)
    check_status(status, body, 0)

    status, body = call("/join_game", userid=110)
    check_status(status, body, GAME_IS_STARTED[0])

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["mission_results"], [])
    check_equal(body["lady"], False)
    check_equal(body["mission_size"], 3)
    check_equal(body["fails_required"], 1)
    check_equal(body["imposition_in"], 5)
    check_equal(body["state"], game.STATE_WAITING_FOR_MISSION)

    print("Propose a mission")
    status, body = call("/vote", userid=100, v=True)
    check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    status, body = call("/propose_mission", userid=101, members=[0, 1, 2])
    check_status(status, body, MUST_BE_LEADER[0])

    status, body = call("/propose_mission", userid=100, members=[0, 1])
    check_status(status, body, WRONG_MISSION_SIZE[0])

    status, body = call("/propose_mission", userid=100, members=[0, 1, 10])
    check_status(status, body, INVALID_PARAMS[0])

    status, body = call("/propose_mission", userid=100, members=[0, 1, 2])
    check_status(status, body, 0)

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["players"][0]["is_member"], True)
    check_equal(body["players"][8]["is_member"], False)
    check_equal(body["lady"], False)
    check_equal(body["state"], game.STATE_WAITING_FOR_VOTES)

    print("Vote")
    for i in range(9):
        status, body = call("/vote", userid=100 + i, v=True)
        check_status(status, body, 0)
        status, body = call("/vote", userid=100 + i, v=True)
        check_status(status, body, HAS_ALREADY_VOTED[0])

    status, body = call("/do_mission", userid=109, v=True)
    check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    status, body = call("/vote", userid=109, v=True)
    check_status(status, body, 0)
    status, body = call("/vote", userid=109, v=True)
    check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["idx"], 0)
    check_equal(body["turn"], 0)
    check_equal(body["lady"], False)
    check_equal(body["state"], game.STATE_MISSION_PENDING)

    print("Participate")

    status, body = call("/do_mission", userid=109, v=True)
    check_status(status, body, MUST_BE_MEMBER[0])

    status, body = call("/do_mission", userid=100, v=True)
    check_status(status, body, 0)

    status, body = call("/do_mission", userid=100, v=True)
    check_status(status, body, HAS_ALREADY_VOTED[0])

    status, body = call("/do_mission", userid=101, v=True)
    check_status(status, body, 0)

    status, body = call("/do_mission", userid=102, v=True)
    check_status(status, body, 0)


    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["idx"], 1)
    check_equal(body["turn"], 1)
    check_equal(body["mission_results"], [True])
    check_equal(body["lady"], False)
    check_equal(body["state"], game.STATE_WAITING_FOR_MISSION)

    print("Turn 2")
    status, body = call("/propose_mission", userid=101, members=[0, 1, 2, 3])
    check_status(status, body, 0)

    for i in range(10):
        status, body = call("/vote", userid=100 + i, v=False)
        check_status(status, body, 0)

    status, body = call("/propose_mission", userid=102, members=[0, 1, 2, 3])
    check_status(status, body, 0)

    for i in range(10):
        status, body = call("/vote", userid=100 + i, v=False)
        check_status(status, body, 0)

    status, body = call("/propose_mission", userid=103, members=[0, 1, 2, 3])
    check_status(status, body, 0)

    for i in range(10):
        status, body = call("/vote", userid=100 + i, v=False)
        check_status(status, body, 0)

    status, body = call("/propose_mission", userid=104, members=[0, 1, 2, 3])
    check_status(status, body, 0)

    for i in range(10):
        status, body = call("/vote", userid=100 + i, v=False)
        check_status(status, body, 0)

    status, body = call("/propose_mission", userid=105, members=[0, 1, 2, 3])
    check_status(status, body, 0)

    for i in range(10):
        status, body = call("/vote", userid=100 + i, v=False)
        check_status(status, body, WRONG_TIME_FOR_ACTION[0]) # Mission is imposed

    for i in range(4):
        status, body = call("/do_mission", userid=100 + i, v=False)
        check_status(status, body, 0)


    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["idx"], 6)
    check_equal(body["turn"], 2)
    check_equal(body["mission_results"], [True, False])
    check_equal(body["lady"], True)
    check_equal(body["state"], game.STATE_WAITING_FOR_MISSION)

    print("Turn 3")
    status, body = call("/propose_mission", userid=106, members=[0, 1, 2, 3], lady=10)
    check_status(status, body, INVALID_PARAMS[0])

    status, body = call("/propose_mission", userid=106, members=[0, 1, 2, 3], lady=6)
    check_status(status, body, INVALID_PARAMS[0])


    status, body = call("/propose_mission", userid=106, members=[0, 1, 2, 3], lady=0)
    check_status(status, body, 0)

    for i in range(10):
        status, body = call("/vote", userid=100 + i, v=True)
        check_status(status, body, 0)

    for i in range(4):
        status, body = call("/do_mission", userid=100 + i, v=True)
        check_status(status, body, 0)

    status, body = call("/kill_merlin", userid=101, target=0)
    check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["idx"], 7)
    check_equal(body["turn"], 3)
    check_equal(body["mission_results"], [True, False, True])
    check_equal(body["lady"], True)
    check_equal(body["state"], game.STATE_WAITING_FOR_MISSION)

    print("Turn 4")
    status, body = call("/propose_mission", userid=107, members=[0, 1, 2, 3, 4], lady=1)
    check_status(status, body, 0)

    for i in range(10):
        status, body = call("/vote", userid=100 + i, v=True)
        check_status(status, body, 0)

    for i in range(5):
        status, body = call("/do_mission", userid=100 + i, v=False)
        check_status(status, body, 0)

    status, body = call("/propose_mission", userid=107, members=[0, 1, 2, 3, 4], lady=2)
    check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["idx"], 7)
    check_equal(body["turn"], 3)
    check_equal(body["mission_results"], [True, False, True, False])
    check_equal(body["lady"], True)
    check_equal(body["state"], game.STATE_LADY)

    status, body = call("/use_lady", userid=102, target=3)
    check_status(status, body, INVALID_PARAMS[0])

    status, body = call("/use_lady", userid=101, target=3)
    check_status(status, body, 0)

    status, body = call("/use_lady", userid=102, target=3)
    check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["mission_results"], [True, False, True, False])
    check_equal(body["lady"], False)
    check_equal(body["state"], game.STATE_WAITING_FOR_MISSION)

    print("Turn 5")
    status, body = call("/propose_mission", userid=108, members=[0, 1, 2, 3, 4])
    check_status(status, body, 0)

    for i in range(10):
        status, body = call("/vote", userid=100 + i, v=True)
        check_status(status, body, 0)

    for i in range(5):
        status, body = call("/do_mission", userid=100 + i, v=True)
        check_status(status, body, 0)

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["idx"], 8)
    check_equal(body["turn"], 4)
    check_equal(body["mission_results"], [True, False, True, False, True])
    check_equal(body["lady"], False)
    check_equal(body["state"], game.STATE_ASSASSIN)

    for i in range(10):
        status, body = call("/kill_merlin", userid=100 + i, target=i)
        #check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    status, body = call("/get_game_state", userid=100)
    check_status(status, body, 0)
    check_equal(body["idx"], 8)
    check_equal(body["turn"], 4)
    check_equal(body["mission_results"], [True, False, True, False, True])
    check_equal(body["good_wins"], True)
    check_equal(body["state"], game.STATE_GAME_FINISHED)

    status, body = call("/propose_mission", userid=107, members=[0, 1, 2, 3, 4], lady=2)
    check_status(status, body, WRONG_TIME_FOR_ACTION[0])

    print("Stats")
    status, body = call("/games")
    check_status(status, body, 0)
    check_equal(body["n_game"], 1)
    id_ = body['games'][0]['id']

    status, body = call("/games/{}".format(id_))
    check_status(status, body, 0)
    r = body['data']
    # print(r)
    s = body['stats']
    # print(s)

    status, body = call("/stats/roles")
    check_status(status, body, 0)
    assert len(body["role_Merlin"]) == 1
    assert len(body["role_Good guy"]) == 4
