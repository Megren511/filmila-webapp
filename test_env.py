from dotenv import load_dotenv
import os
from pathlib import Path
import os

# Get the absolute path to the .env file
env_path = Path(__file__).parent / '.env'

# Clear any existing environment variables
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']
if 'JWT_SECRET_KEY' in os.environ:
    del os.environ['JWT_SECRET_KEY']

# Load from .env file
load_dotenv(dotenv_path=env_path, override=True)

# Run the environment variable generation
from generate_env import generate_env_files
generate_env_files()

# Print the environment variables for verification
print("Environment variables after generation:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')}")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"FRONTEND_URL: {os.getenv('FRONTEND_URL')}")
print(f"REACT_APP_API_URL: {os.getenv('REACT_APP_API_URL')}")

# Print the .env file path and existence
print(f"\n.env file path: {env_path}")
print(f".env file exists: {env_path.exists()}")
if env_path.exists():
    print("\n.env file contents:")
    print(env_path.read_text())
