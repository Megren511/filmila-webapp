from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import stripe
import time

# Import models
from models import Base, User, Film, Purchase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    # Production CORS settings
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

# Configure PostgreSQL
def init_db():
    """Initialize PostgreSQL connection"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Successfully connected to PostgreSQL")
        return SessionLocal()
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        raise

# Initialize database connection
db_session = init_db()

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

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
