import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.base import TimestampMixin

class User(TimestampMixin, db.Model):
    """User model representing Customers, Admins, and Compliance Officers."""
    
    __tablename__ = 'users'

    # Using String(36) for UUID compatibility (SQLite handles this well)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='CUSTOMER')
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, password):
        """Hashes the password and stores it safely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a plain text password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"