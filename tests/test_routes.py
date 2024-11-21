import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Recent Searches' in response.data

def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_register_user(client):
    # Mock form data
    data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'Password@1234',
        'confirm_password': 'Password@1234'
    }
    response = client.post('/register', data=data)
    assert response.status_code == 302  # Redirect to login page

def test_login_user_invalid(client):
    data = {'username': 'nonexistent', 'password': 'wrongpassword'}
    response = client.post('/login', data=data)
    assert response.status_code == 200
    assert b'User does not exist.' in response.data

def test_login_user_success(client, mocker):
    mock_user = {'username': 'testuser', 'password': 'Password@1234', 'user_id': 1}
    mocker.patch('repositories.user_repository.get_user_by_username', return_value=mock_user)
    mocker.patch('flask_bcrypt.check_password_hash', return_value=True)

    data = {'username': 'testuser', 'password': 'Password@1234'}
    response = client.post('/login', data=data)
    assert response.status_code == 302