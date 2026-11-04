def test_register_success(client, init_database):
    res = client.post('/api/auth/register', json={"email": "new@test.com", "password": "pass"})
    assert res.status_code == 201

def test_register_duplicate_email(client, init_database):
    client.post('/api/auth/register', json={"email": "new@test.com", "password": "pass"})
    res = client.post('/api/auth/register', json={"email": "new@test.com", "password": "pass"})
    assert res.status_code == 409

def test_login_success(client, init_database):
    client.post('/api/auth/register', json={"email": "login@test.com", "password": "pass"})
    res = client.post('/api/auth/login', json={"email": "login@test.com", "password": "pass"})
    assert res.status_code == 200
    assert "access_token" in res.get_json()["data"]

def test_login_invalid_password(client, init_database):
    client.post('/api/auth/register', json={"email": "login@test.com", "password": "pass"})
    res = client.post('/api/auth/login', json={"email": "login@test.com", "password": "wrong"})
    assert res.status_code == 401

def test_protected_endpoint_without_token(client, init_database):
    res = client.get('/api/accounts')
    assert res.status_code == 401