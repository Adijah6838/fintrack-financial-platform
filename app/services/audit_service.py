from app import db
from app.models.audit import AuditLog

def log_event(event_type, description, actor_id=None, related_entity_id=None):
    """Helper to create an immutable audit log record."""
    log = AuditLog(
        event_type=event_type,
        description=description,
        actor_id=actor_id,
        related_entity_id=related_entity_id
    )
    db.session.add(log)
    # We don't commit here; the caller commits it along with the business logic.