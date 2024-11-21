import pytest, requests
from app import app
from flask_bcrypt import Bcrypt
from unittest.mock import MagicMock

bcrypt = Bcrypt(app)

user_repository = MagicMock()
meal_repository = MagicMock()

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
    data = {
        'email': 'test4@example.com',
        'username': 'testuser4',
        'password': 'Password@1234',
        'confirm_password': 'Password@1234'
    }
    response = client.post('/register', data=data)
    assert response.status_code == 302

def test_login_user_invalid(client):
    data = {'username': 'nonexistent', 'password': 'wrongpassword'}
    response = client.post('/login', data=data)
    assert response.status_code == 200
    assert b'User does not exist.' in response.data

def test_login_user_success(client, mocker):
    hashed_password = bcrypt.generate_password_hash('Password@1234').decode('utf-8')
    
    mock_user = {'user_id': 15, 'username': 'testuser4', 'password': hashed_password}
    mocker.patch('repositories.user_repository.get_user_by_username', return_value=mock_user)
    
    mocker.patch('flask_bcrypt.check_password_hash', return_value=True)

    data = {'username': 'testuser4', 'password': 'Password@1234'}
    response = client.post('/login', data=data)
    assert response.status_code == 302

def test_login_failure(client):
    user_repository.get_user_by_username.return_value = None
    response = client.post('/login', data={'username': 'nonexistent', 'password': 'Invalid'})
    assert response.status_code == 200  # Stay on login page
    assert b"User does not exist." in response.data

def test_register_user_email_exists(client):
    user_repository.get_user_by_email.return_value = {'email': 'test@example.com'}
    response = client.post('/register', data={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'Valid@123',
        'confirm_password': 'Valid@123'
    })
    assert response.status_code == 200
    assert b"Email is already registered." in response.data

def test_logout(client):
    with client.session_transaction() as session:
        session['user'] = 'testuser'
    response = client.get('/logout')
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert 'user' not in session

def test_foodmeal_post(client, monkeypatch):
    def mock_get(url, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass
            def json(self):
                return {"foods": [{"description": "Apple"}]}
        return MockResponse()
    monkeypatch.setattr(requests, "get", mock_get)
    response = client.post('/foodmeal/', data={"query": "apple"})
    assert response.status_code == 200
    assert b"Apple" in response.data

def test_google_login_redirect(client):
    response = client.get('/google-login')
    assert response.status_code == 302