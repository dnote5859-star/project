# Configuration for the Trucker Profit System (Flask + MongoDB)
import os
from werkzeug.security import generate_password_hash

# MongoDB connection URI (set via environment or defaults to local)
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://dnote5859_db_user:Angel%40786@cluster0.qudkdjc.mongodb.net/trucker_profit"
)


# Flask secret key
SECRET_KEY = os.environ.get("SECRET_KEY", "qwerty12345678")

# Initial exchange rate (USD -> CAD). Admin can update this in the UI.
DEFAULT_EXCHANGE_RATE = float(os.environ.get("DEFAULT_EXCHANGE_RATE", 1.35))

# Admin credentials (in production: use env vars and a proper user collection)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
# Default password "admin123" hashed. Change via env in production.
ADMIN_PASSWORD_HASH = os.environ.get(
    "ADMIN_PASSWORD_HASH",
    generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123"))
)

# File upload location for receipts and photos
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed upload extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}