from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.utils.responses import error_response
from app.utils.permissions import get_current_user
from app.services.transaction_service import execute_transaction

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")

def get_common_payload():
    data = request.get_json() or {}
    return {
        "amount": data.get("amount"),
        "source_acc_num": data.get("source_account_number"),
        "dest_acc_num": data.get("destination_account_number"),
        "idempotency_key": request.headers.get("Idempotency-Key"),
        "description": data.get("description")
    }

@transactions_bp.route("/deposit", methods=["POST"])
@jwt_required()
def deposit():
    user = get_current_user()
    payload = get_common_payload()
    if not payload["dest_acc_num"]:
        return error_response(message="destination_account_number is required.", status_code=400)
    
    return execute_transaction(
        user_id=user.id, transaction_type="DEPOSIT", amount_str=payload["amount"],
        dest_acc_num=payload["dest_acc_num"], idempotency_key=payload["idempotency_key"],
        description=payload["description"]
    )

@transactions_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def withdraw():
    user = get_current_user()
    payload = get_common_payload()
    if not payload["source_acc_num"]:
        return error_response(message="source_account_number is required.", status_code=400)
    
    return execute_transaction(
        user_id=user.id, transaction_type="WITHDRAWAL", amount_str=payload["amount"],
        source_acc_num=payload["source_acc_num"], idempotency_key=payload["idempotency_key"],
        description=payload["description"]
    )

@transactions_bp.route("/transfer", methods=["POST"])
@jwt_required()
def transfer():
    user = get_current_user()
    payload = get_common_payload()
    if not payload["source_acc_num"] or not payload["dest_acc_num"]:
        return error_response(message="Both source and destination account numbers are required.", status_code=400)
    
    return execute_transaction(
        user_id=user.id, transaction_type="TRANSFER", amount_str=payload["amount"],
        source_acc_num=payload["source_acc_num"], dest_acc_num=payload["dest_acc_num"],
        idempotency_key=payload["idempotency_key"], description=payload["description"]
    )