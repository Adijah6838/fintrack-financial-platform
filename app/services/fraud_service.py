from datetime import datetime, timedelta
from app import db
from app.models.transaction import Transaction
from app.models.fraud import FraudAlert, FraudRule
from app.models.account import Account

def evaluate_transaction(transaction):
    """Runs all active fraud rules against a completed transaction."""
    
    # If it's a deposit with no source account, we evaluate the destination account
    target_account_id = transaction.source_account_id or transaction.destination_account_id
    if not target_account_id:
        return

    # 1. LARGE TRANSACTION RULE (Amount > 10,000)
    if transaction.amount >= 10000.00:
        create_alert(
            transaction_id=transaction.id,
            account_id=target_account_id,
            rule="LARGE_TRANSACTION",
            risk="HIGH",
            desc=f"Transaction amount of {transaction.amount} exceeds the 10,000 threshold."
        )

    # 2. RAPID TRANSACTIONS RULE (> 5 txns in 10 mins)
    ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
    recent_txns = Transaction.query.filter(
        Transaction.source_account_id == transaction.source_account_id,
        Transaction.created_at >= ten_mins_ago
    ).count()
    
    if transaction.source_account_id and recent_txns > 5:
        create_alert(
            transaction_id=transaction.id,
            account_id=transaction.source_account_id,
            rule="RAPID_TRANSACTIONS",
            risk="MEDIUM",
            desc=f"Account made {recent_txns} transactions in the last 10 minutes."
        )

    # 3. UNUSUAL PATTERN (Transfers to 3+ distinct accounts in 1 hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    distinct_destinations = db.session.query(Transaction.destination_account_id).filter(
        Transaction.source_account_id == transaction.source_account_id,
        Transaction.transaction_type == 'TRANSFER',
        Transaction.created_at >= one_hour_ago
    ).distinct().count()

    if transaction.transaction_type == 'TRANSFER' and distinct_destinations >= 3:
        create_alert(
            transaction_id=transaction.id,
            account_id=transaction.source_account_id,
            rule="UNUSUAL_PATTERN",
            risk="CRITICAL",
            desc=f"Account transferred to {distinct_destinations} different accounts in 1 hour."
        )

def create_alert(transaction_id, account_id, rule, risk, desc):
    """Helper to safely create and save an alert."""
    alert = FraudAlert(
        transaction_id=transaction_id,
        account_id=account_id,
        rule_triggered=rule,
        risk_level=risk,
        description=desc
    )
    db.session.add(alert)
    # We don't commit here; we let the transaction_service commit everything at once.