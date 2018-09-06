from ayaavalon.database import Role, Vote
from ayaavalon.constants import NAMES
import sqlalchemy as sa
from sqlalchemy import desc
#from sqlalchemy.db.func import count



def get_role_stats(session):
    """
    returns dict containing stats on roles with following keys:

    role_merlin: a list of (userid, count) representing the number of time each player has been merlin.
    role_mordred: ...

    """
    stats = {}

    for role, name in NAMES.items():
        a = session.query(Role.id_player, sa.func.count('*').label('count')) \
            .filter(Role.role == role) \
            .group_by(Role.id_player) \
            .order_by(desc('count'), Role.id_player) \
            .all()
        stats['role_{}'.format(name)] = a

    return stats


def get_connection_stats(session):
    """
    Returns a dict containing two keys 'voted_for' and 'voted_against'.
    Each key contains tuples (id_player, id_target, count).
    """

    stats = {}
    for vote, name in zip([True, False], ['voted_for', 'voted_against']):
        v = session.query(Vote.id_player, Vote.id_target, sa.func.count('*').label('count')) \
            .filter(Vote.vote == vote) \
            .group_by(Vote.id_player, Vote.id_target) \
            .order_by(Vote.id_player, Vote.id_target) \
            .all()
        stats[name] = v

    return stats
