from typing import Any
from repositories.db import get_pool
from psycopg.rows import dict_row

def does_username_exist(username: str) -> bool:
    pool = get_pool

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                        SELECT
                            user_id
                        FROM
                            users
                        WHERE
                            username = %s
                        ''', [username])
            user_id = cur.fetchone()
            return user_id is not None

def get_user_by_username(username: str) -> dict[str, Any] | None:
    pool = get_pool

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                        SELECT
                            user_id,
                            username,
                            password
                        FROM
                            users
                        WHERE
                            username = %s
                        ''', [username])
            user = cur.fetchone()
            return user