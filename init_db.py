from sqlalchemy import create_engine
from models import Base
import os
from dotenv import load_dotenv
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the PostgreSQL database with retry logic"""
    max_retries = 5  # Increased retries for DigitalOcean deployment
    retry_delay = 10  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Database initialization attempt {attempt + 1}/{max_retries}")
            
            # Get database URL
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            
            # Skip if MongoDB URL is found (from old configuration)
            if 'mongodb' in database_url:
                logger.error("Found MongoDB URL - please update DATABASE_URL to PostgreSQL connection string")
                raise ValueError("Invalid database type: MongoDB URL detected, PostgreSQL required")
            
            # Handle potential "postgres://" URLs from DigitalOcean
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            # Create engine with SSL required and TCP keepalive
            engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_pre_ping=True,  # Enable connection health checks
                connect_args={
                    'sslmode': 'require',
                    'keepalives': 1,
                    'keepalives_idle': 30,
                    'keepalives_interval': 10,
                    'keepalives_count': 5
                }
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                logger.info("Database connection test successful")
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("Successfully created all database tables")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to initialize database after all retries")
                raise

if __name__ == "__main__":
    try:
        init_database()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
