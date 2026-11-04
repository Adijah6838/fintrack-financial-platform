def test_get_account_details(client, auth_headers, init_database):
    # Create account
    res = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers)
    acc_id = res.get_json()["data"]["account_id"]
    
    # Fetch it
    res = client.get(f'/api/accounts/{acc_id}', headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["account_id"] == acc_id

def test_zero_amount_rejection(client, auth_headers, init_database):
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    res = client.post('/api/transactions/deposit', json={"amount": 0, "destination_account_number": acc}, headers=auth_headers)
    assert res.status_code == 400
    assert "greater than zero" in res.get_json()["message"]

def test_negative_amount_rejection(client, auth_headers, init_database):
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    res = client.post('/api/transactions/deposit', json={"amount": -50.00, "destination_account_number": acc}, headers=auth_headers)
    assert res.status_code == 400
    assert "greater than zero" in res.get_json()["message"]

def test_invalid_destination_account(client, auth_headers, init_database):
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    client.post('/api/transactions/deposit', json={"amount": 500.00, "destination_account_number": acc}, headers=auth_headers)
    
    # Transfer to a fake account number
    res = client.post('/api/transactions/transfer', json={"amount": 100.00, "source_account_number": acc, "destination_account_number": "0000000000"}, headers=auth_headers)
    assert res.status_code == 404
    assert "Destination account not found" in res.get_json()["message"]

def test_sensitive_info_not_exposed(client, init_database):
    # Register
    res = client.post('/api/auth/register', json={"email": "sec@test.com", "password": "password123"})
    assert "password" not in res.get_json()["data"]
    assert "password_hash" not in res.get_json()["data"]

    # Login
    res = client.post('/api/auth/login', json={"email": "sec@test.com", "password": "password123"})
    user_data = res.get_json()["data"]["user"]
    assert "password" not in user_data
    assert "password_hash" not in user_data

def test_compliance_officer_can_review(client, admin_headers, init_database):
    # Create a compliance officer
    client.post('/api/auth/register', json={"email": "comp@test.com", "password": "pass", "role": "COMPLIANCE_OFFICER"})
    login_res = client.post('/api/auth/login', json={"email": "comp@test.com", "password": "pass"})
    comp_headers = {"Authorization": f"Bearer {login_res.get_json()['data']['access_token']}"}

    # Force an alert as admin/customer first (we need an alert to exist)
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=admin_headers).get_json()["data"]["account_number"]
    client.post('/api/transactions/deposit', json={"amount": 15000.00, "destination_account_number": acc}, headers=admin_headers)
    
    alerts = client.get('/api/fraud/alerts', headers=comp_headers).get_json()["data"]
    alert_id = alerts[0]["alert_id"]

    # Compliance officer reviews it
    res = client.patch(f'/api/fraud/alerts/{alert_id}/review', json={"status": "CONFIRMED"}, headers=comp_headers)
    assert res.status_code == 200

def test_failed_transaction_alert(client, auth_headers, init_database):
    # Note: The Fraud Engine currently only evaluates successful transactions. 
    # This test ensures a failed transaction does NOT create a false positive alert.
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    
    # Try to withdraw without funds (Fails)
    client.post('/api/transactions/withdraw', json={"amount": 100.00, "source_account_number": acc}, headers=auth_headers)
    
    # Check alerts (should be empty)
    res = client.get('/api/fraud/alerts', headers=auth_headers)
    assert len(res.get_json()["data"]) == 0