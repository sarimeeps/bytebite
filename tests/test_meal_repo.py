import pytest
from unittest.mock import MagicMock
from repositories.meal_repository import (
    get_food, get_meal, get_meal_name,
    create_meal, update_meal_name, add_food_to_meal,
    edit_meal, delete_meal, delete_food
)

@pytest.fixture
def mock_db(mocker):
    mock_connection = mocker.patch('psycopg.connect')
    mock_conn_instance = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.return_value.__enter__.return_value = mock_conn_instance
    mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_cursor

def test_get_food(mock_db):
    mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [(1, 'Apple'), (2, 'Banana')]

    meal_id = 1
    foods = get_food(meal_id)

    mock_cursor.execute.assert_called_once_with(
        'SELECT food_id, description FROM food WHERE meal_id = %s', (meal_id,)
    )
    assert foods == [(1, 'Apple'), (2, 'Banana')]

def test_get_meal(mock_db):
    mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [(1, 'Breakfast'), (2, 'Lunch')]

    user_id = 1
    meals = get_meal(user_id)

    mock_cursor.execute.assert_called_once_with(
        'SELECT meal_id, meal_name FROM meal WHERE user_id = %s', (user_id,)
    )
    assert meals == [{'meal_id': 1, 'meal_name': 'Breakfast'}, {'meal_id': 2, 'meal_name': 'Lunch'}]

def test_create_meal(mock_db):
    mock_cursor = mock_db
    mock_cursor.fetchone.return_value = [1]

    user_id = 1
    meal_name = "Dinner"
    meal_id = create_meal(user_id, meal_name)

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO meal (user_id, meal_name) VALUES (%s, %s) RETURNING meal_id",
        (user_id, meal_name)
    )
    assert meal_id == 1

def test_update_meal_name(mock_db):
    mock_cursor = mock_db

    meal_id = 1
    new_meal_name = "Brunch"
    update_meal_name(meal_id, new_meal_name)

    mock_cursor.execute.assert_called_once_with(
        'UPDATE meal SET meal_name = %s WHERE meal_id = %s',
        (new_meal_name, meal_id)
    )

def test_add_food_to_meal(mock_db):
    mock_cursor = mock_db

    meal_id = 1
    fdcId = 12345
    description = "Chicken"
    add_food_to_meal(meal_id, fdcId, description)

    mock_cursor.execute.assert_called_once_with(
        'INSERT INTO food (meal_id, fdcId, description) VALUES (%s, %s, %s)',
        (meal_id, fdcId, description)
    )

def test_edit_meal(mock_db):
    mock_cursor = mock_db

    meal_id = 1
    name = "Lunch"
    ingredients = "Rice, Beans"
    edit_meal(meal_id, name, ingredients)

    mock_cursor.execute.assert_called_once_with(
        'UPDATE meal SET name = %s, ingredients = %s WHERE id = %s',
        (name, ingredients, meal_id)
    )

def test_delete_meal(mock_db):
    mock_cursor = mock_db

    meal_id = 1
    delete_meal(meal_id)

    mock_cursor.execute.assert_called_once_with(
        'DELETE FROM meal WHERE meal_id = %s', (meal_id,)
    )

def test_delete_food(mock_db):
    mock_cursor = mock_db

    meal_id = 1
    food_id = 1
    delete_food(meal_id, food_id)

    mock_cursor.execute.assert_called_once_with(
        'DELETE FROM food WHERE meal_id = %s AND food_id = %s',
        (meal_id, food_id)
    )
    