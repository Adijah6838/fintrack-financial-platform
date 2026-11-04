import json
import uuid
from decimal import Decimal, InvalidOperation
from app import db
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.idempotency import IdempotencyRecord
from app.utils.responses import error_response
from app.services.fraud_service import evaluate_transaction
from app.services.audit_service import log_event

def execute_transaction(user_id, transaction_type, amount_str, source_acc_num=None, dest_acc_num=None, idempotency_key=None, description=None):
    
    # 1. IDEMPOTENCY CHECK
    if idempotency_key:
        existing_record = IdempotencyRecord.query.filter_by(idempotency_key=idempotency_key).first()
        if existing_record:
            return json.loads(existing_record.response_data), existing_record.status_code

    # 2. AMOUNT VALIDATION (Decimal Math Only)
    try:
        amount = Decimal(str(amount_str)).quantize(Decimal('0.01'))
        if amount <= Decimal('0.00'):
            return error_response(message="Amount must be greater than zero.", status_code=400)
    except (InvalidOperation, ValueError):
        return error_response(message="Invalid amount format.", status_code=400)

    try:
        source_account = None
        dest_account = None

        if source_acc_num:
            source_account = Account.query.filter_by(account_number=source_acc_num).with_for_update().first()
            if not source_account or source_account.owner_id != user_id:
                return error_response(message="Source account not found or unauthorized.", status_code=404)
            if source_account.status != 'ACTIVE':
                return error_response(message="Source account is frozen or closed.", status_code=400)

        if dest_acc_num:
            dest_account = Account.query.filter_by(account_number=dest_acc_num).with_for_update().first()
            if not dest_account:
                return error_response(message="Destination account not found.", status_code=404)
            if dest_account.status != 'ACTIVE':
                return error_response(message="Destination account is frozen or closed.", status_code=400)
            if source_account and source_account.id == dest_account.id:
                return error_response(message="Cannot transfer to the same account.", status_code=400)

        # EXECUTE FINANCIAL MOVEMENTS
        if transaction_type in ['WITHDRAWAL', 'TRANSFER']:
            if source_account.balance < amount:
                return error_response(message="Insufficient funds.", status_code=400)
            source_account.balance -= amount

        if transaction_type in ['DEPOSIT', 'TRANSFER']:
            dest_account.balance += amount

        # CREATE LEDGER RECORD
        ref_num = f"TRX-{uuid.uuid4().hex[:8].upper()}"
        new_txn = Transaction(
            reference_number=ref_num,
            transaction_type=transaction_type,
            amount=amount,
            status='COMPLETED',
            description=description,
            source_account_id=source_account.id if source_account else None,
            destination_account_id=dest_account.id if dest_account else None
        )
        db.session.add(new_txn)
        db.session.flush()

        # --- RUN FRAUD DETECTION ---
        evaluate_transaction(new_txn)

        # --- AUDIT LOGGING ---
        log_event(
            event_type=f"{transaction_type}_COMPLETED",
            description=f"{transaction_type} of {amount} completed. Ref: {ref_num}",
            actor_id=user_id,
            related_entity_id=new_txn.id
        )

        # PREPARE RESPONSE
        response_dict = {
            "status": "success",
            "message": f"{transaction_type.capitalize()} successful.",
            "data": {
                "transaction_id": new_txn.id,
                "reference_number": new_txn.reference_number,
                "amount": str(amount),
                "status": new_txn.status,
                "balance": str(source_account.balance if transaction_type != 'DEPOSIT' else dest_account.balance)
            }
        }

        # SAVE IDEMPOTENCY RECORD
        if idempotency_key:
            idemp_record = IdempotencyRecord(
                idempotency_key=idempotency_key,
                user_id=user_id,
                response_data=json.dumps(response_dict),
                status_code=201
            )
            db.session.add(idemp_record)

        db.session.commit()
        return response_dict, 201

    except Exception as e:
        db.session.rollback()
        print(f"Transaction Error: {e}")
        return error_response(message="Transaction failed due to a server error.", status_code=500)