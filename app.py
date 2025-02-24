from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from flask_cors import CORS
import os
import stripe
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Ensure instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)
    logger.info(f"Created instance directory at {instance_path}")

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": os.getenv('ALLOWED_ORIGINS', '*')}})

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_f1lm1l4_w3b4pp_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/filmila.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    logger.info(f"Created upload directory at {app.config['UPLOAD_FOLDER']}")

# Log configuration
logger.info(f"ALLOWED_ORIGINS: {os.getenv('ALLOWED_ORIGINS')}")
logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_filmmaker = db.Column(db.Boolean, default=False)
    films = db.relationship('Film', backref='creator', lazy=True)

class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    film_type = db.Column(db.String(50))
    file_path = db.Column(db.String(255))
    thumbnail_path = db.Column(db.String(255))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_id = db.Column(db.String(120))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/api/films', methods=['GET'])
def get_films():
    films = Film.query.all()
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
@login_required
def upload_film():
    if not current_user.is_filmmaker:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    # Handle file upload and create new Film record
    # Implementation details here
    
    return jsonify({'message': 'Film uploaded successfully'})

@app.route('/api/create-payment-intent', methods=['POST'])
@login_required
def create_payment():
    data = request.json
    film_id = data.get('film_id')
    film = Film.query.get_or_404(film_id)
    
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

@app.route('/api/watch/<int:film_id>', methods=['GET'])
@login_required
def watch_film(film_id):
    purchase = Purchase.query.filter_by(
        user_id=current_user.id,
        film_id=film_id
    ).first()
    
    if not purchase:
        return jsonify({'error': 'Not purchased'}), 403
    
    film = Film.query.get_or_404(film_id)
    return send_file(film.file_path)

# Serve React App
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_path(path):
    if path.startswith('api/'):
        return app.view_functions[path[4:]]()
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
