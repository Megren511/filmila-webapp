from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
import stripe
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from bson import ObjectId
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

# Check required environment variables
required_env_vars = ['MONGODB_URI', 'JWT_SECRET_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins during development
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure MongoDB
client = None
db = None

def test_mongodb_connection():
    """Test MongoDB connection and database operations"""
    try:
        # Test basic connection
        client.admin.command('ping')
        logger.info("✓ MongoDB connection successful")
        
        # Test database access
        db_names = client.list_database_names()
        logger.info(f"✓ Available databases: {db_names}")
        
        # Test filmila database
        filmila_db = client.filmila
        logger.info(f"✓ Connected to database: {filmila_db.name}")
        
        # Test collections
        collections = filmila_db.list_collection_names()
        logger.info(f"✓ Available collections: {collections}")
        
        # Test users collection
        users_count = filmila_db.users.count_documents({})
        logger.info(f"✓ Users collection contains {users_count} documents")
        
        return True, "MongoDB connection and operations successful"
    except Exception as e:
        logger.error(f"MongoDB test failed: {str(e)}")
        logger.exception("Full error traceback:")
        return False, str(e)

def init_mongodb():
    """Initialize MongoDB connection with retry logic"""
    global client, db
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Get MongoDB connection string from environment variable
            mongodb_uri = os.getenv('MONGODB_URI', "mongodb+srv://megrenfilms:qwer050qwer@cluster0.jlezl.mongodb.net/filmila?retryWrites=true&w=majority&appName=Cluster0")
            logger.info(f"Attempting to connect to MongoDB (attempt {attempt + 1}/{max_retries})...")
            
            # Create a new client with timeouts
            client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
            # Get the filmila database
            db = client.filmila
            
            # Ensure indexes exist
            try:
                db.users.create_index([("email", 1)], unique=True)
                logger.info("Email index created/verified")
            except Exception as e:
                logger.warning(f"Index creation warning (can be ignored if index already exists): {str(e)}")
            
            # Ensure collections exist
            required_collections = ['users', 'films']
            for collection in required_collections:
                if collection not in db.list_collection_names():
                    db.create_collection(collection)
                    logger.info(f"Created collection: {collection}")
            
            # Test the connection
            success, message = test_mongodb_connection()
            if success:
                logger.info("MongoDB initialization complete!")
                return client, db
            else:
                raise Exception(f"MongoDB test failed: {message}")
            
        except Exception as e:
            logger.error(f"MongoDB connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All MongoDB connection attempts failed")
                return None, None

# Initialize MongoDB connection
logger.info("Starting MongoDB initialization...")
client, db = init_mongodb()

# Ensure we have a valid database connection
if not client or not db:
    logger.error("Failed to initialize MongoDB. Application may not function correctly.")
else:
    logger.info("MongoDB initialization successful!")

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Configure bcrypt
bcrypt = Bcrypt(app)

# Ensure upload folder exists
if not os.path.exists(app.config.get('UPLOAD_FOLDER', 'uploads')):
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'))
    logger.info(f"Created upload directory at {app.config.get('UPLOAD_FOLDER', 'uploads')}")

# Log configuration
logger.info("MongoDB connected successfully")
logger.info(f"Upload folder: {app.config.get('UPLOAD_FOLDER', 'uploads')}")

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    global client, db
    
    # Verify database connection
    if not client or not db:
        logger.error("No database connection available")
        return jsonify({'message': 'Database connection error. Please try again later.'}), 503

    try:
        data = request.get_json()
        logger.info("Registration attempt received")
        
        # Validate request data
        if not data:
            logger.error("No JSON data received in registration request")
            return jsonify({'message': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logger.error(f"Missing required fields in registration request: {missing_fields}")
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
            
        # Validate email format
        email = data['email']
        if not '@' in email or not '.' in email:
            logger.error(f"Invalid email format: {email}")
            return jsonify({'message': 'Invalid email format'}), 400
            
        # Check if email exists
        try:
            # Try to reconnect if connection was lost
            if not client or not client.is_primary:
                logger.warning("MongoDB connection lost, attempting to reconnect...")
                client, db = init_mongodb()
                if not client or not db:
                    return jsonify({'message': 'Database connection error. Please try again later.'}), 503

            existing_user = db.users.find_one({'email': email})
            if existing_user:
                logger.warning(f"Attempted registration with existing email: {email}")
                return jsonify({'message': 'Email already registered'}), 400
        except Exception as e:
            logger.error(f"Database error while checking existing user: {str(e)}")
            logger.exception("Full traceback for user existence check:")
            return jsonify({'message': 'Database error. Please try again later.'}), 500
            
        # Hash password
        try:
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            logger.debug("Password hashed successfully")
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            return jsonify({'message': 'Error processing password'}), 500
        
        # Prepare user data
        user_data = {
            'name': data.get('name', ''),
            'email': email,
            'password': hashed_password,
            'is_filmmaker': data.get('is_filmmaker', False),
            'created_at': datetime.utcnow()
        }
        
        # Insert user into database
        try:
            result = db.users.insert_one(user_data)
            user_id = str(result.inserted_id)
            logger.info(f"User created successfully with ID: {user_id}")
            
            # Create access token
            try:
                access_token = create_access_token(identity=user_id)
                logger.debug("Access token created successfully")
            except Exception as e:
                logger.error(f"Error creating access token: {str(e)}")
                return jsonify({'message': 'Error creating access token'}), 500
            
            return jsonify({
                'message': 'Registration successful',
                'token': access_token,
                'user': {
                    'id': user_id,
                    'name': user_data['name'],
                    'email': user_data['email'],
                    'is_filmmaker': user_data['is_filmmaker']
                }
            }), 201
            
        except Exception as e:
            logger.error(f"Database error while creating user: {str(e)}")
            logger.exception("Full traceback for user creation:")
            return jsonify({'message': 'Database error. Please try again later.'}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({'message': 'An unexpected error occurred during registration'}), 500

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

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
