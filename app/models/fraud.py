import uuid
from app import db
from app.models.base import TimestampMixin

class FraudRule(TimestampMixin, db.Model):
    """Stores administrator-configured thresholds for fraud detection."""
    __tablename__ = 'fraud_rules'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., LARGE_TRANSACTION
    description = db.Column(db.String(255), nullable=True)
    threshold_value = db.Column(db.Numeric(18, 2), nullable=False)
    time_window_minutes = db.Column(db.Integer, nullable=True) # For rate-limiting rules
    is_active = db.Column(db.Boolean, default=True, nullable=False)

class FraudAlert(TimestampMixin, db.Model):
    """Stores suspicious activity alerts for Compliance Officers to review."""
    __tablename__ = 'fraud_alerts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    transaction_id = db.Column(db.String(36), db.ForeignKey('transactions.id'), nullable=True)
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False, index=True)
    
    rule_triggered = db.Column(db.String(50), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False, default='MEDIUM') # LOW, MEDIUM, HIGH, CRITICAL
    description = db.Column(db.String(255), nullable=False)
    
    # Review Status
    review_status = db.Column(db.String(20), nullable=False, default='NEW') # NEW, UNDER_REVIEW, CONFIRMED, DISMISSED
    reviewed_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)