from functools import wraps  # <-- THIS WAS MISSING
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from app import db
from app.models.user import User
from app.utils.responses import error_response

def get_current_user():
    """Extracts the user ID from the JWT and returns the User object."""
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return None
    # Use the modern SQLAlchemy 2.0 syntax to avoid warnings
    return db.session.get(User, current_user_id)

def admin_required():
    """Decorator to restrict access to ADMIN users only."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "ADMIN":
                return error_response(message="Admin access required.", status_code=403)
            return fn(*args, **kwargs)
        return decorator
    return wrapper