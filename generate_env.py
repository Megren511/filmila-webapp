import secrets
import base64
import json

# Generate a secure JWT secret key
jwt_secret = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

# Use the existing MongoDB URI from the example (you should change this in production)
mongodb_uri = "mongodb+srv://megrenfilms:Wuj9BvI1XxYy3aRz@cluster0.jlezl.mongodb.net/filmila?retryWrites=true&w=majority&appName=Cluster0"

# Create the environment variables
env_vars = {
    "FLASK_APP": "app.py",
    "FLASK_ENV": "production",
    "NODE_ENV": "production",
    "MONGODB_URI": mongodb_uri,
    "JWT_SECRET_KEY": jwt_secret,
    "FRONTEND_URL": "http://localhost:3000",
    "REACT_APP_API_URL": "http://localhost:8080/api",
    "PORT": "8080"
}

# Print the environment variables in a format that can be copied to .env
print("\nHere are your environment variables:\n")
for key, value in env_vars.items():
    print(f"{key}={value}")

print("\nPlease create a .env file with these values.\n")
