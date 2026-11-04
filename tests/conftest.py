import pytest
from app import create_app, db
from app.config import TestingConfig
from app.models.user import User

@pytest.fixture(scope='session')
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db

@pytest.fixture(scope='function')
def auth_headers(client, init_database):
    user_data = {"email": "testuser@example.com", "password": "TestPassword123!", "role": "CUSTOMER"}
    client.post('/api/auth/register', json=user_data)
    login_res = client.post('/api/auth/login', json={"email": user_data["email"], "password": user_data["password"]})
    token = login_res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope='function')
def admin_headers(client, init_database):
    user_data = {"email": "admin@example.com", "password": "AdminPassword123!", "role": "ADMIN"}
    client.post('/api/auth/register', json=user_data)
    login_res = client.post('/api/auth/login', json={"email": user_data["email"], "password": user_data["password"]})
    token = login_res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}