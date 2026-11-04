def test_unauthorized_account_access(client, auth_headers, init_database):
    # Create an account for User A
    res = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers)
    acc_id = res.get_json()["data"]["account_id"]

    # Create a second user
    client.post('/api/auth/register', json={"email": "hacker@test.com", "password": "pass"})
    login_res = client.post('/api/auth/login', json={"email": "hacker@test.com", "password": "pass"})
    hacker_token = login_res.get_json()["data"]["access_token"]
    hacker_headers = {"Authorization": f"Bearer {hacker_token}"}

    # User B tries to access User A's account directly (Should fail with 404)
    res = client.get('/api/accounts', headers=hacker_headers)
    assert len(res.get_json()["data"]) == 0 # Should only see their own 0 accounts

def test_frozen_account_restrictions(client, auth_headers, admin_headers, init_database):
    # Create account
    res = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers)
    acc_id = res.get_json()["data"]["account_id"]
    acc_num = res.get_json()["data"]["account_number"]

    # Admin freezes the account
    client.patch(f'/api/accounts/{acc_id}/status', json={"status": "FROZEN"}, headers=admin_headers)

    # Try to deposit into frozen account
    res = client.post('/api/transactions/deposit', json={"amount": 100.00, "destination_account_number": acc_num}, headers=auth_headers)
    assert res.status_code == 400
    assert "frozen or closed" in res.get_json()["message"]