from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.fraud import FraudAlert
from app.utils.responses import success_response, error_response
from app.services.audit_service import log_event

fraud_bp = Blueprint("fraud", __name__, url_prefix="/api/fraud")

@fraud_bp.route("/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    # Anyone with a valid token can view alerts (for now)
    alerts = FraudAlert.query.order_by(FraudAlert.created_at.desc()).all()
    result = []
    for a in alerts:
        result.append({
            "alert_id": a.id,
            "account_id": a.account_id,
            "rule": a.rule_triggered,
            "risk": a.risk_level,
            "description": a.description,
            "status": a.review_status,
            "created_at": a.created_at.isoformat()
        })
    return success_response(data=result, message="Alerts retrieved.")

@fraud_bp.route("/alerts/<alert_id>/review", methods=["PATCH"])
@jwt_required()
def review_alert(alert_id):
    # Check role FIRST
    claims = get_jwt()
    if claims.get("role") not in ["ADMIN", "COMPLIANCE_OFFICER"]:
        return error_response(message="Compliance or Admin access required.", status_code=403)

    alert = db.session.get(FraudAlert, alert_id)
    if not alert:
        return error_response(message="Alert not found.", status_code=404)
    
    data = request.get_json() or {}
    new_status = data.get("status", "").upper()
    
    if new_status not in ["NEW", "UNDER_REVIEW", "CONFIRMED", "DISMISSED"]:
        return error_response(message="Invalid review status.", status_code=400)

    old_status = alert.review_status
    alert.review_status = new_status
    alert.reviewed_by = get_jwt_identity()

    log_event(
        event_type="ALERT_REVIEWED",
        description=f"Alert {alert_id} changed from {old_status} to {new_status}",
        actor_id=get_jwt_identity(),
        related_entity_id=alert_id
    )
    
    db.session.commit()

    return success_response(message=f"Alert marked as {new_status}.")