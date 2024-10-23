from psycopg_pool import ConnectionPool
from config import get_database_url

pool = None

def get_pool():
    global pool
    if pool is None:
        pool = ConnectionPool(
            conninfo=get_database_url()
        )
    return pool