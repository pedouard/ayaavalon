from alembic.config import Config
from alembic import command
import os

from sqlalchemy.engine import reflection
from sqlalchemy.schema import MetaData, Table, DropTable, ForeignKeyConstraint, DropConstraint
from ayaavalon.database import create_session, engine


def reset_db():
    # create a sqlalchemy session, engine
    session = create_session()

    # drop and recreate tables
    metadata = MetaData()
    db_drop_everything(engine)
    metadata.create_all(engine)

    # run sqlalchemy migrations
    __dir__ = os.path.dirname(os.path.realpath(__file__))
    alembic_cfg = Config(os.path.join(__dir__, "alembic.ini"))
    command.upgrade(alembic_cfg, 'head')



def db_drop_everything(engine):
    # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything

    conn = engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((), (), name=fk['name']))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()