from werkzeug.security import generate_password_hash

DOCKER_IMAGE = "ubuntu"
DOCKER_RUN_KWARGS = {
    "command": "echo hello; echo world"
}

FLASK_SECRET_KEY = "mysecretkey"

AUTH_USERNAME = "admin"
AUTH_PASSWORD = generate_password_hash("password")
