from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.account import Account
from app.utils.responses import success_response, error_response
from app.utils.permissions import get_current_user
from app.services.audit_service import log_event

accounts_bp = Blueprint("accounts", __name__, url_prefix="/api/accounts")

@accounts_bp.route("", methods=["POST"])
@jwt_required()
def create_account():
    user = get_current_user()
    if not user:
        return error_response(message="User not found.", status_code=404)

    data = request.get_json() or {}
    account_type = data.get("account_type", "PERSONAL").upper()
    currency = data.get("currency", "USD").upper()

    if account_type not in ["PERSONAL", "BUSINESS"]:
        return error_response(message="Invalid account type. Must be PERSONAL or BUSINESS.", status_code=400)

    new_account = Account(
        owner_id=user.id,
        account_type=account_type,
        currency=currency
    )
    new_account.account_number = new_account.generate_account_number()

    try:
        db.session.add(new_account)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(message="Failed to create account.", status_code=500)

    return success_response(
        data={
            "account_id": new_account.id,
            "account_number": new_account.account_number,
            "account_type": new_account.account_type,
            "balance": str(new_account.balance),
            "currency": new_account.currency,
            "status": new_account.status
        },
        message="Account created successfully.",
        status_code=201
    )

@accounts_bp.route("", methods=["GET"])
@jwt_required()
def get_user_accounts():
    user = get_current_user()
    if not user:
        return error_response(message="User not found.", status_code=404)

    accounts = Account.query.filter_by(owner_id=user.id).all()
    
    result = []
    for acc in accounts:
        result.append({
            "account_id": acc.id,
            "account_number": acc.account_number,
            "account_type": acc.account_type,
            "balance": str(acc.balance),
            "currency": acc.currency,
            "status": acc.status
        })

    return success_response(data=result, message="Accounts retrieved successfully.")

@accounts_bp.route("/<account_id>", methods=["GET"])
@jwt_required()
def get_account_details(account_id):
    user = get_current_user()
    if not user:
        return error_response(message="User not found.", status_code=404)
        
    account = db.session.get(Account, account_id)
    
    if not account or account.owner_id != user.id:
        return error_response(message="Account not found.", status_code=404)

    return success_response(
        data={
            "account_id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": str(account.balance),
            "currency": account.currency,
            "status": account.status
        },
        message="Account retrieved successfully."
    )

@accounts_bp.route("/<account_id>/status", methods=["PATCH"])
@jwt_required()
def update_account_status(account_id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return error_response(message="Admin access required.", status_code=403)

    account = db.session.get(Account, account_id)
    if not account:
        return error_response(message="Account not found.", status_code=404)

    data = request.get_json() or {}
    new_status = data.get("status", "").upper()

    if new_status not in ["ACTIVE", "FROZEN", "CLOSED"]:
        return error_response(message="Invalid status.", status_code=400)

    old_status = account.status
    account.status = new_status
    
    # Log the event
    log_event(
        event_type="ACCOUNT_STATUS_CHANGED", 
        description=f"Account {account.account_number} changed from {old_status} to {new_status}", 
        actor_id=get_jwt_identity(), 
        related_entity_id=account.id
    )
    
    db.session.commit()
    
    return success_response(message=f"Account status changed to {new_status}") # <-- This was missing or unreachable