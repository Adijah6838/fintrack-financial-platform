import uuid
import random
from app import db
from app.models.base import TimestampMixin

class Account(TimestampMixin, db.Model):
    """Financial Account Model."""
    __tablename__ = 'accounts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_number = db.Column(db.String(10), unique=True, nullable=False, index=True)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    account_type = db.Column(db.String(20), nullable=False, default='PERSONAL')
    currency = db.Column(db.String(3), nullable=False, default='USD')
    balance = db.Column(db.Numeric(18, 2), nullable=False, default=0.00)
    status = db.Column(db.String(20), nullable=False, default='ACTIVE')

    owner = db.relationship('User', backref=db.backref('accounts', lazy=True))

    def generate_account_number(self):
        while True:
            number = str(random.randint(1000000000, 9999999999))
            if not Account.query.filter_by(account_number=number).first():
                return number

    def __repr__(self):
        return f"<Account {self.account_number} (Balance: {self.balance})>"