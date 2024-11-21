import pytest
from unittest.mock import patch
from repositories.user_repository import (
    does_username_exist,
    create_user,
    create_oauth_user,
    get_user_by_email,
    get_user_id_by_email,
    get_user_by_username,
    get_user_by_id,
    get_all_users
)

@pytest.fixture
def mock_db(mocker):
    mock_connection = mocker.patch('repositories.user_repository.get_pool')
    mock_cursor = mocker.MagicMock()
    mock_connection.return_value.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_cursor, mock_connection

def test_does_username_exist(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = (1,)
    result = does_username_exist('exampleuser')
    assert result is True

    mock_cursor.fetchone.return_value = None
    result = does_username_exist('nonexistentuser')
    assert result is False

def test_create_user(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = (123,)
    email = 'example@example.com'
    username = 'exampleuser'
    password = 'password123'
    
    result = create_user(email, username, password)
    
    assert result['user_id'] == 123
    assert result['username'] == username

def test_create_user_failure(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(Exception):
        create_user('example@example.com', 'exampleuser', 'password123')

def test_create_oauth_user(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = (123,)
    email = 'example@example.com'
    username = 'exampleuser'

    create_oauth_user(username, email)

    mock_cursor.execute.assert_called_once_with('''
                        INSERT INTO users (email, username)
                        VALUES (%s, %s)
                        RETURNING user_id
                        ''', [email, username])

def test_get_user_by_email(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = {'user_id': 123, 'username': 'exampleuser', 'password': 'password123'}
    result = get_user_by_email('example@example.com')
    
    assert result['user_id'] == 123
    assert result

def test_get_user_id_by_email(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = {'user_id': 123}
    result = get_user_id_by_email('example@example.com')
    
    assert result['user_id'] == 123
    assert result

def test_get_user_by_username(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = {'user_id': 123, 'username': 'exampleuser', 'password': 'password123'}
    result = get_user_by_username('exampleuser')
    
    assert result['user_id'] == 123
    assert result

def test_get_user_by_id(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = {'user_id': 123, 'username': 'exampleuser'}
    result = get_user_by_id(123)
    
    assert result['user_id'] == 123
    assert result

def test_get_all_users(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchall.return_value = [
        {'user_id': 123, 'username': 'exampleuser'},
        {'user_id': 124, 'username': 'anotheruser'}
    ]
    result = get_all_users()
    
    assert len(result) == 2
    assert result[0]['user_id'] == 123
    assert result[1]['user_id'] == 124
