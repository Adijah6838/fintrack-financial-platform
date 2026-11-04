from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from app import db
from app.models.user import User
from app.utils.responses import success_response, error_response
from app.services.audit_service import log_event

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    if not data or not data.get("email") or not data.get("password"):
        return error_response(message="Email and password are required.", status_code=400)
    
    email = data["email"].strip().lower()
    password = data["password"]
    role = data.get("role", "CUSTOMER").upper()

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return error_response(message="A user with this email already exists.", status_code=409)

    new_user = User(email=email, role=role)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.flush() # Flush to get the user ID
        log_event("USER_REGISTERED", f"New user registered: {email}", actor_id=new_user.id, related_entity_id=new_user.id)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(message="An error occurred while creating the user.", status_code=500)

    return success_response(
        data={"id": new_user.id, "email": new_user.email, "role": new_user.role},
        message="User registered successfully.",
        status_code=201
    )

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return error_response(message="Email and password are required.", status_code=400)

    email = data["email"].strip().lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        # Log failed attempt
        log_event("LOGIN_FAILED", f"Failed login attempt for: {email}", related_entity_id=None)
        db.session.commit()
        return error_response(message="Invalid email or password.", status_code=401)

    if not user.is_active:
        return error_response(message="Account is deactivated.", status_code=403)

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    # Log successful login
    log_event("USER_LOGIN", f"Successful login for: {email}", actor_id=user.id, related_entity_id=user.id)
    db.session.commit()

    return success_response(
        data={"access_token": access_token, "user": {"id": user.id, "email": user.email, "role": user.role}},
        message="Login successful."
    )