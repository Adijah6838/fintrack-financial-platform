def test_customer_cannot_access_admin_dashboard(client, auth_headers):
    res = client.get('/api/admin/overview', headers=auth_headers)
    assert res.status_code == 403

def test_customer_cannot_review_fraud_alerts(client, auth_headers):
    res = client.patch('/api/fraud/alerts/fake-id/review', json={"status": "CONFIRMED"}, headers=auth_headers)
    # The role check happens before the ID check
    assert res.status_code == 403