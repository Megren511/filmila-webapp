import os
import sys
import logging
from dotenv import load_dotenv
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment configuration...")
if os.path.exists('.env'):
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
else:
    logger.info("No .env file found, using environment variables from system")

# Verify required environment variables
required_vars = ['DATABASE_URL', 'JWT_SECRET_KEY', 'SECRET_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

logger.info("Environment configuration verified successfully")

if __name__ == "__main__":
    try:
        port = int(os.getenv('PORT', 8080))
        logger.info(f"Starting application on port {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
