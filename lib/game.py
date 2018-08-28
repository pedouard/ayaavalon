# -*- coding: UTF-8 -*
import time
import random
import json
import numpy as np
from datetime import datetime, timedelta

from withings.datascience.core import config
from lib.db.database import Player, Game
from www import status

from withings.datascience.core.flask_utils import WithingsException


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



class Player():

    def __init__(self, p, is_host):
        self.userid = p.userid_player
        self.is_host = is_host
        self.role = None

        self.is_member = None
        self.has_voted = None
        self.has_voted = None
        self.has_participated = None
        self.participation = None
        self.has_lady = None


    def reset(self):
        self.is_member = False

        self.has_voted = False
        self.vote = False

        self.has_participated = False
        self.participation = False

        self.has_lady = False


    def dump(self):
        return {
            "userid": self.userid,
            "is_host": self.is_host,
            "is_member": self.is_member,
            "has_voted": self.has_voted,
            "has_voted": self.has_voted,
            "has_participated": self.has_participated,
            "participation": self.participation,
            "has_lady": self.has_lady,
        }


    def format_info(self, players):
        big_data = {
            "bad_guys": [],
            "merligana": [],
            "friends": [],
            "role": self.role
        }

        if self.role == MERLIN:
            for i, p in enumerate(players):
                if p.role in [MORGANA, ASSASSIN, BADGUY, OBERON]:
                    big_data["bad_guys"].append(i)

        if self.role == PERCI:
            for i, p in enumerate(players):
                if p.role in [MERLIN, MORGANA]:
                    big_data["merligana"].append(i)

        if self.role in [MORGANA, BADGUY, ASSASSIN, MORDRED]:
            for i, p in enumerate(players):
                if p.role in [MORGANA, BADGUY, ASSASSIN, MORDRED]:
                    big_data["friends"].append(i)

        return big_data


    def is_good(self):
        return self.role < 10


class Game():

    def __init__(self, session):
        self.session = session
        self.players = []
        self.nplayers = 0

        self.is_started = False
        self.turn = 0

        self.idx = 0

        self.mission_results = []
        self.mission_is_proposed = None
        self.mission_is_started = None
        self.waiting_for_assassination = False

        self.game_setup = None

        self.lady = False
        self.mission_size = None
        self.fails_required = None
        self.imposition_in = None

        self.good_wins = None

    def dump(self, p):
        big_data = {
            "players": [p.dump() for p in self.players],
            "nplayers": self.nplayers,
            "is_started": self.is_started,

            "turn": self.turn,
            "idx": self.idx,

            "mission_results": self.mission_results,
            "mission_is_proposed": self.mission_is_proposed,
            "mission_is_started": self.mission_is_started,
            "waiting_for_assassination": self.waiting_for_assassination,

            "game_setup": self.game_setup,
            "lady": self.lady,
            "mission_size": self.mission_size,
            "fails_required": self.fails_required,
            "imposition_in": self.imposition_in,

            "good_wins": self.good_wins,

            "self": {}
        }

        if p:
            big_data["self"] = p.format_info(self.players)

        return big_data


    def add_player(self, p):
        if self.is_started:
            raise WithingsException(*status.GAME_IS_STARTED)

        if self._get_by_userid(p.userid_player):
            raise WithingsException(*status.ALREADY_IN_THE_GAME)

        if self.nplayers == 10:
            raise WithingsException(*status.GAME_IS_FULL)

        self.players.append(Player(p, is_host=(self.nplayers == 0)))
        self.nplayers = len(self.players)


    def start(self, p):
        if self.is_started:
            raise WithingsException(*status.GAME_IS_STARTED)

        if not p.is_host:
            raise WithingsException(*status.MUST_BE_HOST)

        if self.nplayers not in GAME_SETUPS:
            raise WithingsException(*status.NOT_ENOUGH_PLAYERS)

        self.game_setup = GAME_SETUPS[self.nplayers]

        characters = self.game_setup["characters"]
        random.shuffle(characters)
        for i, p in enumerate(self.players):
            p.role = characters[i]

        self.is_started = True
        self._start_new_turn()


    def propose_mission(self, p, members, lady):
        if not self.is_started:
            raise WithingsException(*status.GAME_MUST_BE_STARTED)

        if self.players[self.idx].userid != p.userid:
            raise WithingsException(*status.MUST_BE_LEADER)

        if len(members) != self.mission_size:
            raise WithingsException(*status.WRONG_MISSION_SIZE)

        if np.max(members) > self.nplayers - 1 or np.min(members) < 0 or len(members) != len(set(members)):
            raise WithingsException(*status.INVALID_PARAMS)

        if self.mission_is_proposed or self.mission_is_started:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if self.lady and (lady < 0 or lady > len(members) or self.players[lady].userid == p.userid):
            raise WithingsException(*status.INVALID_PARAMS)

        self.mission_is_proposed = True
        for id_ in members:
            self.players[id_].is_member = True

        if self.lady:
            self.players[lady].has_lady = True

        if self.imposition_in == 1:
            # Imposition !
            self.mission_is_started = 1


    def vote(self, p, v):
        if not self.is_started:
            raise WithingsException(*status.GAME_MUST_BE_STARTED)

        if not self.mission_is_proposed or self.mission_is_started:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if p.has_voted:
            raise WithingsException(*status.HAS_ALREADY_VOTED)

        p.has_voted = True
        p.vote = v

        self._resolve_votes()


    def do_mission(self, p, v):
        if not self.is_started:
            raise WithingsException(*status.GAME_MUST_BE_STARTED)

        if not self.mission_is_started:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if not p.is_member:
            raise WithingsException(*status.MUST_BE_MEMBER)

        if p.has_participated:
            raise WithingsException(*status.HAS_ALREADY_VOTED)

        p.has_participated = True
        p.participation = v

        self._resolve_participations()


    def assassinate(self, p, target):
        if not self.is_started:
            raise WithingsException(*status.GAME_MUST_BE_STARTED)

        if not self.waiting_for_assassination:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if not p.role == ASSASSIN or p.role == MORGANA:
            raise WithingsException(*status.INVALID_PARAMS)

        self.waiting_for_assassination = False
        if self.players[target].role == MERLIN:
            self.good_wins = False
        else:
            self.good_wins = True

        self._end()


    def _start_new_turn(self):
        gs = self.game_setup
        self.mission_size = gs["missions"][self.turn]
        self.fails_required = gs["fails"][self.turn]
        self.imposition_in = gs["imposition_at"]

        self.mission_is_proposed = False
        self.mission_is_started = False

        self._reset_players()

        self.lady = len([res for res in self.mission_results if not res]) == 1 and gs["lady"]


    def _get_by_userid(self, userid):
        for p in self.players:
            if userid == p.userid:
                return p

        return False


    def _reset_players(self):
        for p in self.players:
            p.reset()


    def _resolve_votes(self):
        for p in self.players:
            if not p.has_voted:
                return

        # All players have voted !

        votes_for = np.sum([p.vote for p in self.players])
        if votes_for > self.nplayers / 2.0:
            # Mission accepted
            self.mission_is_started = True
        else:
            # Mission refused
            self._reset_players()
            self.mission_is_proposed = False
            self.idx = (self.idx+1) % self.nplayers
            self.imposition_in -= 1


    def _resolve_participations(self):
        for p in self.players:
            if p.is_member and not p.has_participated:
                return

        # All players have participated !

        fails = len([p.participation for p in self.players if p.is_member and not p.participation])

        if fails >= self.fails_required:
            # Mission failed
            self.mission_results.append(False)
        else:
            # Mission succeded
            self.mission_results.append(True)

        self._assess_game_end()

        if not self.waiting_for_assassination:
            self.idx = (self.idx+1) % self.nplayers
            self.turn += 1
            self._start_new_turn()


    def _assess_game_end(self):
        if len([res for res in self.mission_results if res]) == 3:
            # Good wins !
            self.waiting_for_assassination = True

        elif len([res for res in self.mission_results if not res]) == 3:
            # Evil wins :()
            self.good_wins = False
            self._end()


    def _end(self):
        self.is_started = False


