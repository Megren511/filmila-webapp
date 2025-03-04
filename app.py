from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
import logging
from pymongo import MongoClient
from bson import ObjectId
import stripe
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check required environment variables
required_vars = ['MONGODB_URI', 'JWT_SECRET_KEY']
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
                "https://filmila-webapp.onrender.com",
                "https://filmila-webapp.vercel.app"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

# Configure bcrypt
bcrypt = Bcrypt(app)

# Configure MongoDB
client = None
db = None

def init_mongodb():
    """Initialize MongoDB connection with retry logic"""
    import os
    from pymongo import MongoClient
    import logging
    from time import sleep

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Get MongoDB URI from environment variable
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        logger.error("MONGODB_URI environment variable is not set!")
        raise ValueError("MONGODB_URI environment variable is not set")

    # Log connection attempt (no sensitive data)
    logger.info("Attempting to connect to MongoDB...")
    
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            # Create MongoDB client with timeouts
            client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test the connection
            client.admin.command('ping')
            
            # Get database and create indexes
            db = client.get_database("filmila")
            db.users.create_index([("email", 1)], unique=True)
            
            logger.info("Successfully connected to MongoDB")
            return client, db

        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"MongoDB connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to MongoDB after {max_retries} attempts")
                raise

# Initialize MongoDB connection
client, db = init_mongodb()

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
        existing_user = db.users.find_one({'email': email})
        if existing_user:
            return jsonify({'message': 'Email already registered'}), 400

        # Create user document
        user_data = {
            'name': data.get('name', '').strip(),
            'email': email,
            'password': bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            'is_filmmaker': data.get('is_filmmaker', False),
            'created_at': datetime.utcnow()
        }

        # Insert into database
        result = db.users.insert_one(user_data)
        user_id = str(result.inserted_id)

        # Generate token
        token = create_access_token(identity=user_id)

        # Return success response
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': user_id,
                'name': user_data['name'],
                'email': user_data['email'],
                'is_filmmaker': user_data['is_filmmaker']
            }
        }), 200

    except Exception as e:
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
            
        user = db.users.find_one({'email': data['email']})
        logger.info(f"User found: {bool(user)}")
        
        if user and bcrypt.check_password_hash(user['password'], data['password']):
            access_token = create_access_token(identity=str(user['_id']))
            logger.info(f"Login successful for user: {user['email']}")
            return jsonify({
                'message': 'Login successful',
                'token': access_token,
                'user': {
                    'id': str(user['_id']),
                    'email': user['email'],
                    'is_filmmaker': user.get('is_filmmaker', False)
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
    current_user_id = get_jwt_identity()
    user = db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    return jsonify({
        'id': str(user['_id']),
        'email': user['email'],
        'is_filmmaker': user.get('is_filmmaker', False)
    })

# Film routes
@app.route('/api/films', methods=['GET'])
def get_films():
    films = db.films.find()
    return jsonify([{
        'id': str(film['_id']),
        'title': film['title'],
        'description': film['description'],
        'price': film['price'],
        'film_type': film['film_type'],
        'thumbnail_path': film['thumbnail_path'],
        'creator_id': str(film['creator_id'])
    } for film in films])

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_film():
    current_user_id = get_jwt_identity()
    user = db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user.get('is_filmmaker'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    # Rest of your upload logic here
    return jsonify({'message': 'Upload successful'}), 200

@app.route('/api/films/<film_id>', methods=['GET'])
@jwt_required()
def get_film(film_id):
    film = db.films.find_one({'_id': ObjectId(film_id)})
    if not film:
        return jsonify({'error': 'Film not found'}), 404
        
    return jsonify({
        'id': str(film['_id']),
        'title': film['title'],
        'description': film['description'],
        'price': film['price'],
        'film_type': film['film_type'],
        'thumbnail_path': film['thumbnail_path'],
        'creator_id': str(film['creator_id'])
    })

# Payment routes
@app.route('/api/create-payment', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.json
    film_id = data.get('film_id')
    film = db.films.find_one({'_id': ObjectId(film_id)})
    
    if not film:
        return jsonify({'error': 'Film not found'}), 404
    
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(film['price'] * 100),  # Convert to cents
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
    purchase = db.purchases.find_one({
        'user_id': ObjectId(current_user_id),
        'film_id': ObjectId(film_id)
    })
    
    if not purchase:
        return jsonify({'error': 'Not purchased'}), 403
        
    film = db.films.find_one({'_id': ObjectId(film_id)})
    if not film:
        return jsonify({'error': 'Film not found'}), 404
        
    return send_file(film['file_path'])

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
