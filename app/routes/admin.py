from flask import Blueprint
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.fraud import FraudAlert
from app.models.audit import AuditLog
from app.utils.permissions import admin_required
from app.utils.responses import success_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/overview", methods=["GET"])
@admin_required()
def get_overview():
    """Aggregate platform statistics for the Admin Dashboard."""
    
    # 1. User & Account Metrics
    total_users = User.query.count()
    active_accounts = Account.query.filter_by(status='ACTIVE').count()
    
    # 2. Transaction Metrics
    # Coalesce handles the case where there are 0 transactions (returns 0.00 instead of None)
    total_volume = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.00)).filter(Transaction.status == 'COMPLETED').scalar()
    successful_txns = Transaction.query.filter_by(status='COMPLETED').count()
    failed_txns = Transaction.query.filter_by(status='FAILED').count()
    pending_txns = Transaction.query.filter_by(status='PENDING').count()

    # 3. Fraud Metrics
    total_flagged = FraudAlert.query.count()
    high_risk_alerts = FraudAlert.query.filter(FraudAlert.risk_level.in_(['HIGH', 'CRITICAL'])).count()

    # 4. Chart Data: Transaction Volume (Last 7 Days)
    # We do a simple group-by in SQLite. (This syntax is largely compatible with PostgreSQL too).
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    volume_by_day = db.session.query(
        func.date(Transaction.created_at).label('date'),
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.created_at >= seven_days_ago,
        Transaction.status == 'COMPLETED'
    ).group_by(func.date(Transaction.created_at)).all()

    chart_volume = [{"date": str(row.date), "amount": float(row.amount)} for row in volume_by_day]

    # 5. Recent Activity (Tables)
    recent_txns = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    recent_audits = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(5).all()

    recent_txns_data = [{
        "reference": t.reference_number,
        "type": t.transaction_type,
        "amount": str(t.amount),
        "status": t.status,
        "created_at": t.created_at.isoformat()
    } for t in recent_txns]

    recent_audits_data = [{
        "event": a.event_type,
        "description": a.description,
        "created_at": a.created_at.isoformat()
    } for a in recent_audits]

    # --- Build the Response ---
    return success_response(
        data={
            "stats": {
                "total_users": total_users,
                "active_accounts": active_accounts,
                "total_volume": str(total_volume),
                "successful_transactions": successful_txns,
                "failed_transactions": failed_txns,
                "pending_transactions": pending_txns,
                "total_flagged": total_flagged,
                "high_risk_alerts": high_risk_alerts
            },
            "charts": {
                "volume_by_day": chart_volume
            },
            "recent_transactions": recent_txns_data,
            "recent_audit_logs": recent_audits_data
        },
        message="Admin overview retrieved successfully."
    )

@admin_bp.route("/users", methods=["GET"])
@admin_required()
def get_all_users():
    users = User.query.all()
    result = [{"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active} for u in users]
    return success_response(data=result, message="All users retrieved.")

@admin_bp.route("/audit-logs", methods=["GET"])
@admin_required()
def get_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    result = [{
        "id": l.id,
        "actor_id": l.actor_id,
        "event_type": l.event_type,
        "description": l.description,
        "created_at": l.created_at.isoformat()
    } for l in logs]
    return success_response(data=result, message="Audit logs retrieved.")