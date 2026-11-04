from app.services.processing_service import process_pending_transactions
from app.models.transaction import Transaction
from app import db

def test_background_worker_processes_pending(client, auth_headers, app, init_database):
    acc = client.post('/api/accounts', json={"account_type": "PERSONAL"}, headers=auth_headers).get_json()["data"]["account_number"]
    
    with app.app_context():
        # Manually create a PENDING transaction
        txn = Transaction(
            reference_number="TRX-PENDING-123",
            transaction_type="DEPOSIT",
            amount=500.00,
            status="PENDING",
            destination_account_id=acc
        )
        db.session.add(txn)
        db.session.commit()
        
        # Run the worker
        processed = process_pending_transactions()
        assert processed == 1
        
        # Check status
        updated_txn = Transaction.query.filter_by(reference_number="TRX-PENDING-123").first()
        assert updated_txn.status == "COMPLETED"