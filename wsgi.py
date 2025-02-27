import os
from dotenv import load_dotenv
from app import app

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
