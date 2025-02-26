from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
import stripe
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": os.getenv('ALLOWED_ORIGINS', '*')}}, supports_credentials=True)
bcrypt = Bcrypt(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'filmila-secret-key-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb+srv://megrenfilms:2sL22BvuWR9Bkqan@cluster0.jlezl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Initialize extensions
mongo = PyMongo(app)
jwt = JWTManager(app)

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    logger.info(f"Created upload directory at {app.config['UPLOAD_FOLDER']}")

# Log configuration
logger.info("MongoDB connected successfully")
logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'message': 'Email already registered'}), 400
        
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    user_data = {
        'email': data['email'],
        'password': hashed_password,
        'is_filmmaker': data.get('is_filmmaker', False),
        'created_at': datetime.utcnow()
    }
    
    try:
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = str(result.inserted_id)
        
        # Create access token
        access_token = create_access_token(identity=str(result.inserted_id))
        
        return jsonify({
            'message': 'Registration successful',
            'token': access_token,
            'user': {
                'id': str(result.inserted_id),
                'email': user_data['email'],
                'is_filmmaker': user_data['is_filmmaker']
            }
        }), 201
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'An error occurred during registration'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    user = mongo.db.users.find_one({'email': data['email']})
    
    if user and bcrypt.check_password_hash(user['password'], data['password']):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'is_filmmaker': user.get('is_filmmaker', False)
            }
        }), 200
    
    return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user_id = get_jwt_identity()
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
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
    films = mongo.db.films.find()
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
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user.get('is_filmmaker'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    # Rest of your upload logic here
    return jsonify({'message': 'Upload successful'}), 200

@app.route('/api/films/<film_id>', methods=['GET'])
@jwt_required()
def get_film(film_id):
    film = mongo.db.films.find_one({'_id': ObjectId(film_id)})
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
    film = mongo.db.films.find_one({'_id': ObjectId(film_id)})
    
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
    purchase = mongo.db.purchases.find_one({
        'user_id': ObjectId(current_user_id),
        'film_id': ObjectId(film_id)
    })
    
    if not purchase:
        return jsonify({'error': 'Not purchased'}), 403
        
    film = mongo.db.films.find_one({'_id': ObjectId(film_id)})
    if not film:
        return jsonify({'error': 'Film not found'}), 404
        
    return send_file(film['file_path'])

# Serve React App
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
