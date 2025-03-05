import os
import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure secret key."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_env_files():
    """Generate .env and .env.production files with secure environment variables."""
    # Common variables
    env_vars = {
        'FLASK_APP': 'app.py',
        'PORT': '8080',
        'FRONTEND_URL': 'http://localhost:3000',
        'REACT_APP_API_URL': 'http://localhost:8080/api'
    }

    # Development-specific variables
    dev_vars = {
        'FLASK_ENV': 'development',
        'NODE_ENV': 'development',
        'DATABASE_URL': 'sqlite:///filmila.db',  # SQLite for development
        'JWT_SECRET_KEY': generate_secret_key(),
        'SECRET_KEY': generate_secret_key()
    }

    # Production-specific variables
    prod_vars = {
        'FLASK_ENV': 'production',
        'NODE_ENV': 'production',
        'DATABASE_URL': 'YOUR_PRODUCTION_DATABASE_URL',  # Replace with your production database URL
        'JWT_SECRET_KEY': generate_secret_key(),
        'SECRET_KEY': generate_secret_key(),
        'FRONTEND_URL': 'https://filmila-webapp.onrender.com',
        'REACT_APP_API_URL': 'https://filmila-webapp.onrender.com/api'
    }

    # Create .env file for development
    with open('.env', 'w') as f:
        for key, value in {**env_vars, **dev_vars}.items():
            f.write(f'{key}={value}\n')

    # Create .env.production file
    with open('.env.production', 'w') as f:
        for key, value in prod_vars.items():  # Use only prod vars for production
            f.write(f'{key}={value}\n')

    print('Generated .env successfully!')
    print('Generated .env.production successfully!')
    print('\nNOTE: Replace YOUR_PRODUCTION_DATABASE_URL in .env.production with your actual database URL')

if __name__ == '__main__':
    generate_env_files()
