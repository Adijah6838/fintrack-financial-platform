def test_rapid_transactions_alert(client, auth_headers, init_database):
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    client.post('/api/transactions/deposit', json={"amount": 10000.00, "destination_account_number": acc}, headers=auth_headers)
    
    # Make 6 rapid withdrawals (Threshold is >5)
    for i in range(6):
        headers = auth_headers.copy()
        headers["Idempotency-Key"] = f"rapid-key-{i}"
        client.post('/api/transactions/withdraw', json={"amount": 10.00, "source_account_number": acc}, headers=headers)
    
    res = client.get('/api/fraud/alerts', headers=auth_headers)
    alerts = res.get_json()["data"]
    assert any(a["rule"] == "RAPID_TRANSACTIONS" for a in alerts)

def test_review_fraud_alert(client, auth_headers, admin_headers, init_database):
    # Force a large transaction to generate an alert
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    client.post('/api/transactions/deposit', json={"amount": 15000.00, "destination_account_number": acc}, headers=auth_headers)
    
    # Get alert ID
    alerts = client.get('/api/fraud/alerts', headers=auth_headers).get_json()["data"]
    alert_id = alerts[0]["alert_id"]

    # Compliance officer (Admin for now) reviews it
    res = client.patch(f'/api/fraud/alerts/{alert_id}/review', json={"status": "CONFIRMED"}, headers=admin_headers)
    assert res.status_code == 200
    
    # Verify status changed
    updated_alerts = client.get('/api/fraud/alerts', headers=auth_headers).get_json()["data"]
    assert updated_alerts[0]["status"] == "CONFIRMED"