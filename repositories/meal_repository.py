from typing import Any
from repositories.db import get_pool, get_database_url
from psycopg.rows import dict_row
import psycopg

def create_meal(name, ingredients):
    # CHANGE
    with psycopg.connect(
        conninfo=get_database_url()
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
            'INSERT INTO meals (name, ingredients, favorite) VALUES (%s, %s, %s)',
            (name, ingredients, False)
            )

def edit_meal(meal_id, name, ingredients):
    # CHANGE
    with psycopg.connect(
        conninfo=get_database_url()
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE meals SET name = %s, ingredients = %s WHERE id = %s',
                (name, ingredients, meal_id)
            )

def delete_meal(meal_id):
# CHANGE
    with psycopg.connect(
        conninfo=get_database_url()
    ) as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM meals WHERE id = %s', (meal_id,)
                        )