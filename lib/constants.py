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
        "imposition_at": 4,
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

STATE_EMPTY = 0
STATE_NOT_STARTED = 1
STATE_WAITING_FOR_MISSION = 2
STATE_WAITING_FOR_VOTES = 3
STATE_MISSION_PENDING = 4
STATE_LADY = 5
STATE_ASSASSIN = 6
STATE_GAME_FINISHED = 7
