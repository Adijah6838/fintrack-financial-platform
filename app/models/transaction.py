import uuid
from app import db
from app.models.base import TimestampMixin

class Transaction(TimestampMixin, db.Model):
    """Records all financial movements."""
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # A human-readable reference number (e.g., TRX-8F9A2B)
    reference_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    transaction_type = db.Column(db.String(20), nullable=False) # DEPOSIT, WITHDRAWAL, TRANSFER
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    status = db.Column(db.String(20), nullable=False, default='COMPLETED') # PENDING, COMPLETED, FAILED, etc.
    description = db.Column(db.String(255), nullable=True)

    # Source and Destination accounts (nullable because a deposit has no source)
    source_account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=True, index=True)
    destination_account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=True, index=True)

    def __repr__(self):
        return f"<Transaction {self.reference_number} | {self.transaction_type} | {self.amount}>"