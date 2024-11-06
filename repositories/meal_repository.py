from typing import Any
from repositories.db import get_pool, get_database_url
from psycopg.rows import dict_row
import psycopg

def get_food(meal_id):
    with psycopg.connect(conninfo=get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT fdcId, description FROM food WHERE meal_id = %s',
                (meal_id,)
            )
            foods = cur.fetchall()
            return foods


def create_meal(user_id, meal_name="New Meal"):
    with psycopg.connect(conninfo=get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO meal (user_id, meal_name) VALUES (%s, %s) RETURNING meal_id",
                (user_id, meal_name)
            )
            meal_id = cur.fetchone()[0]
            conn.commit()
            return meal_id


def update_meal_name(meal_id, meal_name):
    with psycopg.connect(conninfo=get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE meal SET meal_name = %s WHERE meal_id = %s',
                (meal_name, meal_id)
            )

def add_food_to_meal(meal_id, fdcId, description):
    with psycopg.connect(conninfo=get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO food (meal_id, fdcId, description) VALUES (%s, %s, %s)',
                (meal_id, fdcId, description)
            )

def edit_meal(meal_id, name, ingredients):
    # CHANGE
    with psycopg.connect(
        conninfo=get_database_url()
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE meal SET name = %s, ingredients = %s WHERE id = %s',
                (name, ingredients, meal_id)
            )

def delete_meal(meal_id):
# CHANGE
    with psycopg.connect(
        conninfo=get_database_url()
    ) as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM meal WHERE id = %s', (meal_id,)
                        )