import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test PostgreSQL connection and basic operations"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable is not set")
            return False
            
        # Handle potential "postgres://" URLs from DigitalOcean
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        logger.info("Testing database connection...")
        logger.info(f"Database host: {database_url.split('@')[1].split('/')[0]}")
        
        # Create engine with SSL required
        engine = create_engine(
            database_url,
            pool_size=1,
            max_overflow=0,
            connect_args={'sslmode': 'require', 'connect_timeout': 10}
        )
        
        # Test connection and basic query
        with engine.connect() as conn:
            # Test SELECT
            logger.info("Testing SELECT query...")
            result = conn.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                logger.info("SELECT query successful")
            
            # Test database version
            logger.info("Getting PostgreSQL version...")
            result = conn.execute(text("SELECT version()")).fetchone()
            logger.info(f"Database version: {result[0]}")
            
            # Test current database name
            logger.info("Getting current database name...")
            result = conn.execute(text("SELECT current_database()")).fetchone()
            logger.info(f"Current database: {result[0]}")
            
            # Test SSL status
            logger.info("Checking SSL status...")
            result = conn.execute(text("SHOW ssl")).fetchone()
            logger.info(f"SSL enabled: {result[0]}")
            
        logger.info("All connection tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
