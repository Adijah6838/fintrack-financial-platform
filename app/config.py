import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-key-do-not-use-in-prod")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-jwt-key-do-not-use-in-prod")
    
    # JWT Settings
    jwt_expires_hours = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 8))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=jwt_expires_hours)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///fintrack_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Fraud Engine Settings
    FRAUD_LARGE_AMOUNT_THRESHOLD = os.environ.get("FRAUD_LARGE_AMOUNT_THRESHOLD", "10000.00")
    FRAUD_RAPID_TXN_COUNT = int(os.environ.get("FRAUD_RAPID_TXN_COUNT", 5))
    FRAUD_RAPID_TXN_WINDOW_MINUTES = int(os.environ.get("FRAUD_RAPID_TXN_WINDOW_MINUTES", 10))
    FRAUD_PATTERN_DESTINATIONS = int(os.environ.get("FRAUD_PATTERN_DESTINATIONS", 3))
    FRAUD_PATTERN_WINDOW_MINUTES = int(os.environ.get("FRAUD_PATTERN_WINDOW_MINUTES", 60))
    FRAUD_FAILED_ATTEMPTS_THRESHOLD = int(os.environ.get("FRAUD_FAILED_ATTEMPTS_THRESHOLD", 3))

    # Background Worker
    WORKER_MAX_RETRIES = int(os.environ.get("WORKER_MAX_RETRIES", 3))
    WORKER_POLL_INTERVAL_SECONDS = int(os.environ.get("WORKER_POLL_INTERVAL_SECONDS", 5))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "this-is-a-much-longer-test-secret-key-for-testing" # <-- Updated
    WTF_CSRF_ENABLED = False
class ProductionConfig(Config):
    DEBUG = False