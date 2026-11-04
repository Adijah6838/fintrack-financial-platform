def test_create_account(client, auth_headers, init_database):
    res = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers)
    assert res.status_code == 201

def test_deposit_success(client, auth_headers, init_database):
    acc_res = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers)
    acc_num = acc_res.get_json()["data"]["account_number"]
    res = client.post('/api/transactions/deposit', json={"amount": 500.00, "destination_account_number": acc_num}, headers=auth_headers)
    assert res.status_code == 201
    assert res.get_json()["data"]["balance"] == "500.00"

def test_withdraw_insufficient_funds(client, auth_headers, init_database):
    acc_res = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers)
    acc_num = acc_res.get_json()["data"]["account_number"]
    res = client.post('/api/transactions/withdraw', json={"amount": 100.00, "source_account_number": acc_num}, headers=auth_headers)
    assert res.status_code == 400

def test_transfer_success_and_atomicity(client, auth_headers, init_database):
    acc1 = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    acc2 = client.post('/api/accounts', json={"account_type": "BUSINESS"}, headers=auth_headers).get_json()["data"]["account_number"]
    
    client.post('/api/transactions/deposit', json={"amount": 1000.00, "destination_account_number": acc1}, headers=auth_headers)
    res = client.post('/api/transactions/transfer', json={"amount": 400.00, "source_account_number": acc1, "destination_account_number": acc2}, headers=auth_headers)
    assert res.status_code == 201
    
    accounts = client.get('/api/accounts', headers=auth_headers).get_json()["data"]
    for a in accounts:
        if a["account_number"] == acc1: assert a["balance"] == "600.00"
        if a["account_number"] == acc2: assert a["balance"] == "400.00"

def test_idempotency(client, auth_headers, init_database):
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    headers = auth_headers.copy()
    headers["Idempotency-Key"] = "unique-key-123"
    payload = {"amount": 100.00, "destination_account_number": acc}
    
    res1 = client.post('/api/transactions/deposit', json=payload, headers=headers)
    res2 = client.post('/api/transactions/deposit', json=payload, headers=headers)
    
    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res2.get_json()["data"]["balance"] == "100.00" # Didn't double deposit

def test_unusual_transfer_pattern_fraud_alert(client, auth_headers, init_database):
    acc1 = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    acc2 = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    
    # Deposit 20,000 so we have enough funds for the 15,000 transfer
    client.post('/api/transactions/deposit', json={"amount": 20000.00, "destination_account_number": acc1}, headers=auth_headers)
    
    # Transfer 15,000 (This will trigger the LARGE_TRANSACTION rule)
    client.post('/api/transactions/transfer', json={"amount": 15000.00, "source_account_number": acc1, "destination_account_number": acc2}, headers=auth_headers)
    
    res = client.get('/api/fraud/alerts', headers=auth_headers)
    alerts = res.get_json()["data"]
    assert len(alerts) > 0
    assert any(a["rule"] == "LARGE_TRANSACTION" for a in alerts)