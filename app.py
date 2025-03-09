from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import stripe
import time
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
Base = declarative_base()

# Define models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_filmmaker = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Film(Base):
    __tablename__ = 'films'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    price = Column(Float)
    film_type = Column(String)
    thumbnail_path = Column(String)
    creator_id = Column(Integer, ForeignKey('users.id'))
    file_path = Column(String)

class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    film_id = Column(Integer, ForeignKey('films.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

# Check required environment variables
required_vars = ['DATABASE_URL', 'JWT_SECRET_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Configure Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='/')

# Configure CORS based on environment
if os.getenv('FLASK_ENV') == 'development':
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
else:
    # Production CORS settings for DigitalOcean
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://sea-turtle-app-879b6.ondigitalocean.app"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return str(user_id)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    try:
        user_id = jwt_data["sub"]
        return db_session.query(User).filter_by(id=int(user_id)).first()
    except (KeyError, ValueError):
        return None

# Configure bcrypt
bcrypt = Bcrypt(app)

# Configure database
def init_db():
    """Initialize database connection with retry logic"""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Initializing database connection (attempt {attempt + 1}/{max_retries})...")
            
            # Get database URL from environment
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            
            # Handle potential "postgres://" URLs from DigitalOcean
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            logger.info(f"Using PostgreSQL database: {database_url.split('@')[1]}")
            
            # PostgreSQL-specific settings
            engine_args = {
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
                'pool_recycle': 1800,  # Recycle connections every 30 minutes
                'echo': False,  # SQL logging disabled in production
                'connect_args': {
                    'connect_timeout': 10,  # Connection timeout in seconds
                    'sslmode': 'require'    # Enforce SSL
                }
            }
            
            engine = create_engine(database_url, **engine_args)
            
            # Test the connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                if result and result[0] == 1:
                    logger.info("Successfully connected to database")
                else:
                    raise Exception("Database connection test failed")
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            
            # Create session factory
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return SessionLocal()
            
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection failed (attempt {attempt + 1}): {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to database after all retries")
                raise
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise

# Initialize database session
try:
    db_session = init_db()
    logger.info("Database initialization completed successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

# Serve React static files
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

# Authentication routes
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Check content type
        if not request.is_json:
            return jsonify({'message': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        # Log request data (excluding password)
        safe_data = {k: v for k, v in data.items() if k != 'password'}
        logger.info(f"Registration request received: {safe_data}")
        
        # Validate required fields
        required_fields = ['email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Validate email format
        email = data.get('email', '').strip()
        if not '@' in email or not '.' in email:
            return jsonify({'message': 'Invalid email format'}), 400

        # Check if user exists
        existing_user = db_session.query(User).filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'Email already registered'}), 400

        # Create user document
        user_data = User(
            name=data.get('name', '').strip(),
            email=email,
            password=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            is_filmmaker=data.get('is_filmmaker', False),
            created_at=datetime.utcnow()
        )

        # Insert into database
        db_session.add(user_data)
        db_session.commit()
        user_id = user_data.id

        # Generate token
        token = create_access_token(identity=str(user_id))
        logger.info(f"Created access token for user {user_id}")

        # Return success response
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': user_id,
                'name': user_data.name,
                'email': user_data.email,
                'is_filmmaker': user_data.is_filmmaker
            }
        }), 200

    except Exception as e:
        db_session.rollback()
        logger.error(f"Registration error: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({'message': 'Server error during registration'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        logger.info(f"Login attempt for email: {data.get('email')}")
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing email or password'}), 400
            
        user = db_session.query(User).filter_by(email=data['email']).first()
        logger.info(f"User found: {bool(user)}")
        
        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=str(user.id))
            logger.info(f"Login successful for user: {user.email}")
            return jsonify({
                'message': 'Login successful',
                'token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'is_filmmaker': user.is_filmmaker
                }
            }), 200
        
        logger.info("Invalid credentials")
        return jsonify({'message': 'Invalid email or password'}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'An error occurred during login'}), 500

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Getting user profile for ID: {current_user_id}")
        
        user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not user:
            logger.warning(f"User not found for ID: {current_user_id}")
            return jsonify({'message': 'User not found'}), 404
            
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_filmmaker': user.is_filmmaker
        })
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        return jsonify({'message': 'Error retrieving user data'}), 500

# Film routes
@app.route('/api/films', methods=['GET'])
def get_films():
    films = db_session.query(Film).all()
    return jsonify([{
        'id': film.id,
        'title': film.title,
        'description': film.description,
        'price': film.price,
        'film_type': film.film_type,
        'thumbnail_path': film.thumbnail_path,
        'creator_id': film.creator_id
    } for film in films])

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_film():
    current_user_id = get_jwt_identity()
    user = db_session.query(User).filter_by(id=current_user_id).first()
    
    if not user.is_filmmaker:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    # Rest of your upload logic here
    return jsonify({'message': 'Upload successful'}), 200

@app.route('/api/films/<film_id>', methods=['GET'])
@jwt_required()
def get_film(film_id):
    film = db_session.query(Film).filter_by(id=film_id).first()
    if not film:
        return jsonify({'error': 'Film not found'}), 404
        
    return jsonify({
        'id': film.id,
        'title': film.title,
        'description': film.description,
        'price': film.price,
        'film_type': film.film_type,
        'thumbnail_path': film.thumbnail_path,
        'creator_id': film.creator_id
    })

# Payment routes
@app.route('/api/create-payment', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.json
    film_id = data.get('film_id')
    film = db_session.query(Film).filter_by(id=film_id).first()
    
    if not film:
        return jsonify({'error': 'Film not found'}), 404
    
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(film.price * 100),  # Convert to cents
            currency='usd'
        )
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/watch/<film_id>', methods=['GET'])
@jwt_required()
def watch_film(film_id):
    current_user_id = get_jwt_identity()
    purchase = db_session.query(Purchase).filter_by(user_id=current_user_id, film_id=film_id).first()
    
    if not purchase:
        return jsonify({'error': 'Not purchased'}), 403
        
    film = db_session.query(Film).filter_by(id=film_id).first()
    if not film:
        return jsonify({'error': 'Film not found'}), 404
        
    return send_file(film.file_path)

@app.route('/api/payments', methods=['POST'])
@jwt_required()
def create_payment():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        film_id = data['film_id']
        
        film = db_session.query(Film).filter_by(id=film_id).first()
        if not film:
            return jsonify({'message': 'Film not found'}), 404
            
        # Record the purchase
        purchase = Purchase(
            user_id=int(current_user),
            film_id=film_id,
            amount=film.price,
            purchase_date=datetime.utcnow()
        )
        
        db_session.add(purchase)
        db_session.commit()
        
        return jsonify({
            'message': 'Payment successful',
            'purchase_id': purchase.id
        }), 200
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error processing payment: {str(e)}")
        return jsonify({'message': 'Server error processing payment'}), 500

@app.route('/api/films/<int:film_id>/watch', methods=['GET'])
@jwt_required()
def watch_film(film_id):
    try:
        current_user = get_jwt_identity()
        
        # Check if user has purchased the film
        purchase = db_session.query(Purchase).filter_by(
            user_id=int(current_user),
            film_id=film_id
        ).first()
        
        if not purchase:
            return jsonify({'message': 'Film not purchased'}), 403
            
        film = db_session.query(Film).filter_by(id=film_id).first()
        if not film:
            return jsonify({'message': 'Film not found'}), 404
            
        return send_file(film.file_path)
    except Exception as e:
        logger.error(f"Error accessing film: {str(e)}")
        return jsonify({'message': 'Server error accessing film'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
