from app import db
from app.models.transaction import Transaction
from app.models.audit import AuditLog

def process_pending_transactions():
    """Worker function to process PENDING transactions."""
    pending_txns = Transaction.query.filter_by(status='PENDING').all()
    processed_count = 0
    
    for txn in pending_txns:
        try:
            # Simulate processing (e.g., sending to external bank)
            txn.status = 'COMPLETED'
            
            log = AuditLog(
                event_type="TXN_PROCESSED",
                description=f"Background worker processed {txn.reference_number}",
                related_entity_id=txn.id
            )
            db.session.add(log)
            db.session.commit()
            processed_count += 1
        except Exception as e:
            db.session.rollback()
            txn.status = 'FAILED'
            db.session.commit()
            
    return processed_count