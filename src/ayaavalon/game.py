# -*- coding: UTF-8 -*
import random

from withings.datascience.core.flask_utils import WithingsException

from ayaavalon.database import Game as GameDatabase
from ayaavalon.database import add_game_stats
from ayaavalon.www import status
from ayaavalon.constants import *


# TODO implement Galahad
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

    @property
    def __version__(self):
        return 0

    def __init__(self, session):
        self.session = session
        self.players = []
        self.nplayers = 0
        self.n_mission_before_imposition = None

        self.state = STATE_EMPTY
        self.turn = 0

        self.idx = 0

        self.mission_results = []

        self.game_setup = None

        self.lady = False
        self.mission_size = None
        self.fails_required = None
        self.imposition_in = None

        self.good_wins = None

        self.game_log = {
            'players': [],
            'roles': [],

            'host': [],
            'game_setup': [],

            'turn': [],
            'good_wins': None,
        }

    def dump_state(self, p):
        """ Dump game state for a player. """
        big_data = {
            "players": [p.dump() for p in self.players],
            "nplayers": self.nplayers,
            "state": self.state,

            "turn": self.turn,
            "idx": self.idx,
            "mission_results": self.mission_results,

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


    def dump_full_game(self):
        """ Dump full game into a dict, must be called after game is finished. """

        if self.state != STATE_GAME_FINISHED:
            raise Exception('Game is not finished, cannot dump full infos.')

        return self.game_log


    def add_player(self, p):
        if self.state not in [STATE_EMPTY, STATE_NOT_STARTED]:
            raise WithingsException(*status.GAME_IS_STARTED)

        if self._get_by_userid(p.userid_player):
            raise WithingsException(*status.ALREADY_IN_THE_GAME)

        if self.nplayers == 10:
            raise WithingsException(*status.GAME_IS_FULL)

        self.state = STATE_NOT_STARTED
        self.players.append(Player(p, is_host=(self.nplayers == 0)))
        self.nplayers = len(self.players)


    def start(self, p):
        if self.state not in [STATE_NOT_STARTED]:
            raise WithingsException(*status.GAME_IS_STARTED)

        if not p.is_host:
            raise WithingsException(*status.MUST_BE_HOST)

        if self.nplayers not in GAME_SETUPS:
            raise WithingsException(*status.NOT_ENOUGH_PLAYERS)

        self.game_setup = GAME_SETUPS[self.nplayers]
        self.n_mission_before_imposition = self.game_setup['imposition_at']

        characters = self.game_setup["characters"]
        random.shuffle(characters)
        for i, p in enumerate(self.players):
            p.role = characters[i]
            self.game_log['players'].append(p.userid)
            self.game_log['roles'].append(p.role)

        self._start_new_turn()

        self.game_log['game_setup'] = self.game_setup
        self.game_log['host'] = p.userid


    def propose_mission(self, p, members, lady):
        if self.state != STATE_WAITING_FOR_MISSION:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if self.players[self.idx].userid != p.userid:
            raise WithingsException(*status.MUST_BE_LEADER)

        if len(members) != self.mission_size:
            raise WithingsException(*status.WRONG_MISSION_SIZE)

        if max(members) > self.nplayers - 1 or min(members) < 0 or len(members) != len(set(members)):
            raise WithingsException(*status.INVALID_PARAMS)

        if self.lady and (lady < 0 or lady > len(members) or self.players[lady].userid == p.userid):
            raise WithingsException(*status.INVALID_PARAMS)

        self.state = STATE_WAITING_FOR_VOTES
        for id_ in members:
            self.players[id_].is_member = True

        if self.lady:
            self.players[lady].has_lady = True

        if self.imposition_in == 1:
            self.state = STATE_MISSION_PENDING

        id_mission = self.n_mission_before_imposition - self.imposition_in

        self.game_log['turn'][-1]['missions'].append({
            'id_mission': id_mission,
            'arthur': p.userid,
            'members': [self.players[m].userid for m in members],

            'votes': [],
            'accepted': -1,  # -1 imposed, 0 refused, 1 accepted

            'who_failed': [],
            'fails': None,
            'success': None,

            'has_lady': self.lady,
            'lady': self.players[lady].userid if self.lady else None,
            'used_lady_on': None,
            'lady_claimed_to_see': None,
        })

    def vote(self, p, v):
        if not self.state == STATE_WAITING_FOR_VOTES:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if p.has_voted:
            raise WithingsException(*status.HAS_ALREADY_VOTED)

        p.has_voted = True
        p.vote = v

        self._resolve_votes()


    def do_mission(self, p, v):
        if not self.state == STATE_MISSION_PENDING:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if not p.is_member:
            raise WithingsException(*status.MUST_BE_MEMBER)

        if p.has_participated:
            raise WithingsException(*status.HAS_ALREADY_VOTED)

        p.has_participated = True
        p.participation = v

        self._resolve_participations()


    def assassinate(self, p, target):
        if self.state != STATE_ASSASSIN:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if not p.role == ASSASSIN or p.role == MORGANA:
            raise WithingsException(*status.INVALID_PARAMS)

        self.state = STATE_GAME_FINISHED
        if self.players[target].role == MERLIN:
            self.good_wins = False
            self.game_log['merlin_killed'] = 1
        else:
            self.good_wins = True
            self.game_log['merlin_killed'] = 0
        self.game_log['merlin_targeted'] = self.players[target].userid

        self._end()


    def use_lady(self, p, target):
        if self.state != STATE_LADY:
            raise WithingsException(*status.WRONG_TIME_FOR_ACTION)

        if not p.has_lady:
            raise WithingsException(*status.INVALID_PARAMS)

        self.game_log['turn'][-1]['missions'][-1]['used_lady_on'] = self.players[target].userid

        self.idx = (self.idx+1) % self.nplayers
        self.turn += 1
        self._start_new_turn()
        return self.players[target].role in [PEON, MERLIN, PERCI]


    def _start_new_turn(self):
        gs = self.game_setup
        self.mission_size = gs["missions"][self.turn]
        self.fails_required = gs["fails"][self.turn]
        self.imposition_in = gs["imposition_at"]

        self.state = STATE_WAITING_FOR_MISSION
        self._reset_players()

        # Lady of the lake must be distributed ?
        self.lady = len([res for res in self.mission_results if not res]) == 1 and gs["lady"]

        self.game_log['turn'].append({'missions': []})


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

        votes_for = sum([p.vote for p in self.players])
        if votes_for > self.nplayers / 2.0:
            # Mission accepted
            self.state = STATE_MISSION_PENDING
            self.game_log['turn'][-1]['missions'][-1]['accepted'] = 1
        else:
            # Mission refused
            self._reset_players()
            self.state = STATE_WAITING_FOR_MISSION
            self.idx = (self.idx+1) % self.nplayers
            self.imposition_in -= 1
            self.game_log['turn'][-1]['missions'][-1]['accepted'] = 0

        self.game_log['turn'][-1]['missions'][-1]['votes'] = [p.has_voted for p in self.players]


    def _resolve_participations(self):
        for p in self.players:
            if p.is_member and not p.has_participated:
                return

        # All players have participated !

        fails = len([p.participation for p in self.players if p.is_member and not p.participation])
        success = len([p.participation for p in self.players if p.is_member and p.participation])
        self.game_log['turn'][-1]['missions'][-1]['fails'] = fails
        self.game_log['turn'][-1]['missions'][-1]['success'] = success
        self.game_log['turn'][-1]['missions'][-1]['who_failed'] = [p.userid for p in self.players if p.is_member and not p.participation]

        if fails >= self.fails_required:
            # Mission failed
            self.mission_results.append(False)
            if self.lady:
                self.state = STATE_LADY
        else:
            # Mission succeded
            self.mission_results.append(True)

        self._assess_game_end()

        if self.state not in [STATE_ASSASSIN, STATE_LADY]:
            self.idx = (self.idx+1) % self.nplayers
            self.turn += 1
            self._start_new_turn()


    def _assess_game_end(self):
        if len([res for res in self.mission_results if res]) == 3:
            # Good wins !
            self.state = STATE_ASSASSIN

        elif len([res for res in self.mission_results if not res]) == 3:
            # Evil wins :()
            self.good_wins = False
            self.state = STATE_GAME_FINISHED
            self._end()


    def _end(self):
        self.game_log['good_wins'] = self.good_wins
        self.is_started = False

        d = self.dump_full_game()
        v = self.__version__
        game_record = GameDatabase(info=d, version=v)
        self.session.add(game_record)
        self.session.commit()
        print('added game record', d)

        add_game_stats(game_record.id_game, d, self.session)
        print('added stats record')
