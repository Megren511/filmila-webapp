from dotenv import load_dotenv
import os
from pathlib import Path

# Get the absolute path to the .env file
env_path = Path(__file__).parent / '.env'

# Clear any existing environment variables
if 'MONGODB_URI' in os.environ:
    del os.environ['MONGODB_URI']

# Load from .env file
load_dotenv(dotenv_path=env_path, override=True)

print("Environment variables:")
print(f"MONGODB_URI: {os.getenv('MONGODB_URI')}")
print(f"JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')}")
print(f"FRONTEND_URL: {os.getenv('FRONTEND_URL')}")
print(f"PORT: {os.getenv('PORT')}")
print(f"DEBUG: {os.getenv('DEBUG')}")

# Print the .env file path and existence
print(f"\n.env file path: {env_path}")
print(f".env file exists: {env_path.exists()}")
if env_path.exists():
    print("\n.env file contents:")
    print(env_path.read_text())
