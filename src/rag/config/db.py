import os
from dotenv import load_dotenv
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool
from qdrant_client import QdrantClient


load_dotenv()


qdrant = QdrantClient(url=os.getenv('QDRANT_URL'))


DB_RULES = "rules"
DB_DOK_KLAIM = "dok-klaim-multi-vector"
DB_JENIS_BERKAS = "jenis_berkas"


pool_simpp = ConnectionPool(
    open=True,
    kwargs={
        "host": os.getenv("DB_HOST_SIMPP"),
        "port": os.getenv("DB_PORT_SIMPP"),
        "dbname": os.getenv("DB_NAME_SIMPP"),
        "user": os.getenv("DB_USER_SIMPP"),
        "password": os.getenv("DB_PASS_SIMPP"),
        "autocommit": True,
        "row_factory": namedtuple_row,
    },
)


def db_simpp():
    return pool_simpp.connection()
