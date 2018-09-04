from ayaavalon.database import Role
from ayaavalon.constants import NAMES
import sqlalchemy as sa
#from sqlalchemy.db.func import count



def get_role_stats(session):
    """
    returns dict containing stats on roles with following keys:

    role_merlin: a list of (userid, count) representing the number of time each player has been merlin.
    role_mordred: ...

    """

    r = session.query(Role)

    stats = {}

    for role, name in NAMES.items():
        a = session.query(Role.id_player, sa.func.count('*')) \
            .filter(Role.role == role) \
            .group_by(Role.id_player).all()
        stats['role_{}'.format(name)] = a

    return stats
