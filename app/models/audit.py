import uuid
from datetime import datetime
from app import db

class AuditLog(db.Model):
    """Immutable record of important system events."""
    __tablename__ = 'audit_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True) # Nullable for anonymous events (e.g., failed login)
    
    event_type = db.Column(db.String(50), nullable=False, index=True) # e.g., USER_LOGIN, TRANSFER_COMPLETED
    related_entity_id = db.Column(db.String(36), nullable=True) # e.g., Transaction ID, Account ID
    description = db.Column(db.String(255), nullable=False)
    
    # Note: We do NOT use the TimestampMixin here. Audit logs should not have an "updated_at".
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)