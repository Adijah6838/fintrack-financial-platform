from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    return render_template("login.html")

@views_bp.route("/register")
def register_page():
    return render_template("register.html")

@views_bp.route("/dashboard")
def dashboard_page():
    return render_template("customer_dashboard.html")

@views_bp.route("/admin")
def admin_page():
    return render_template("admin_dashboard.html")