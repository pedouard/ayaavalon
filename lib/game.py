# -*- coding: UTF-8 -*
import time
import random
import json
from datetime import datetime, timedelta

from withings.datascience.core import config
from lib.db.database import Player, Game
from www import status

MERLIN = 0
PERCI = 1
GALAHAD = 2
PEON = 3
MORDRED = 10
MORGANA = 11
OBERON = 12
ASSASSIN = 13
BADGUY = 14

NAMES = {
    MERLIN: "Merlin",
    PERCI: "Percival",
    GALAHAD: "Galahad",
    PEON: "Good guy",
    MORDRED: "Mordred",
    MORGANA: "Morgana",
    OBERON: "Oberon",
    ASSASSIN: "Assassin",
    BADGUY: "Bad Guy",
}

GAME_SETUPS = {
    2: {
        "missions": [1, 2, 1, 1, 2],
        "fails": [1, 1, 1, 1, 1],
        "imposition_at": 4,
        "lady": False,
        "characters": [PEON, BADGUY]
    },
    5: {
        "missions": [2, 3, 2, 3, 3],
        "fails": [1, 1, 1, 1, 1],
        "imposition_at": 5,
        "lady": False,
        "characters": [MERLIN, PERCI, PEON, MORDRED, MORGANA]
    },
    6: {
        "missions": [2, 3, 4, 3, 4],
        "fails": [1, 1, 1, 1, 1],
        "imposition_at": 5,
        "lady": False,
        "characters": [MERLIN, PERCI, PEON, PEON, MORDRED, MORGANA]
    },
    7: {
        "missions": [2, 3, 3, 4, 4],
        "fails": [1, 1, 1, 2, 1],
        "imposition_at": 5,
        "lady": True,
        "characters": [MERLIN, PERCI, PEON, PEON, MORDRED, MORGANA, ASSASSIN]
    },
    8: {
        "missions": [3, 4, 4, 5, 5],
        "fails": [1, 1, 1, 2, 1],
        "imposition_at": 5,
        "lady": True,
        "characters": [MERLIN, PERCI, PEON, PEON, PEON, MORDRED, MORGANA, ASSASSIN]
    },
    9: {
        "missions": [3, 4, 4, 5, 5],
        "fails": [1, 1, 1, 2, 1],
        "imposition_at": 5,
        "lady": False,
        "characters": [MERLIN, PERCI, PEON, PEON, PEON, PEON, MORDRED, MORGANA, ASSASSIN]
    },
    10: {
        "missions": [3, 4, 4, 5, 5],
        "fails": [1, 1, 1, 2, 1],
        "imposition_at": 5,
        "lady": True,
        "characters": [MERLIN, PERCI, PEON, PEON, PEON, PEON, MORDRED, MORGANA, ASSASSIN, OBERON]
    },

}

def is_good(id_):
    return id_ < 10


class Player():

    def __init__(self, p, is_host):
        self.userid = p.userid_player
        self.is_host = is_host
        self.role = None


class Game():

    def __init__(self):
        self.players = []
        self.nplayers = 0

        self.is_started = False
        self.turn = 0
        self.idx = 0

        self.startdate = datetime.now()
        self.enddate = None
        self.host = None

        self.turn_logs = []

        self.missions = None
        self.fails = None
        self.lady = None
        self.imposition_at = None


    def add_player(self, p):
        self.players.append(Player(p, is_host=(self.nplayers == 0)))
        self.nplayers = len(self.players)


    def start(self):
        game_setup = GAME_SETUPS[self.nplayers]
        self.missions = game_setup["missions"]
        self.fails = game_setup["fails"]
        self.lady = game_setup["lady"]
        self.imposition_at = game_setup["imposition_at"]

        characters = game_setup["characters"]
        random.shuffle(characters)
        for i, p in enumerate(self.players):
            p.role = characters[i]

        self.is_started = True


    def end(self):
        pass # send json to the database


    def _get_by_userid(self, userid):
        for p in self.players:
            if userid == p.userid:
                return p

        return False



