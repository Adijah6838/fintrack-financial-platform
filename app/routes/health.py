from flask import Blueprint, jsonify

# Create a Blueprint named 'health'
health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint to verify the API is running."""
    return jsonify({
        "status": "success",
        "message": "FINTRACK API is operational",
        "data": {
            "version": "1.0.0",
            "environment": "development"
        }
    }), 200