import uuid
from app import db
from app.models.base import TimestampMixin

class IdempotencyRecord(TimestampMixin, db.Model):
    __tablename__ = 'idempotency_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    response_data = db.Column(db.Text, nullable=False) 
    status_code = db.Column(db.Integer, nullable=False, default=200) # <-- MUST BE HERE