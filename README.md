# Filmila - Independent Filmmaker Platform

A platform for independent filmmakers to share their work and monetize their content through pay-per-view streaming.

## Features

- Film upload for creators
- Pay-per-view system
- Secure payment processing with Stripe
- Beautiful gallery-style homepage
- Film categorization
- User authentication for both filmmakers and viewers
- PostgreSQL database for reliable data storage

## Project Structure

```
filmila-webapp/
├── app.py                 # Flask backend
├── models.py             # SQLAlchemy models
├── requirements.txt       # Python dependencies
├── uploads/              # Film storage directory
└── frontend/            # React frontend
    ├── src/
    │   ├── components/  # Reusable UI components
    │   ├── pages/      # Page components
    │   └── App.js      # Main React component
    └── package.json    # Frontend dependencies
```

## Setup Instructions

1. Set up PostgreSQL:
```bash
# Install PostgreSQL if not already installed
# Create a new database
createdb filmila_db

# Or using psql
psql
CREATE DATABASE filmila_db;
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (use generate_env.py)
python generate_env.py
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Run the application:
```bash
# Terminal 1 - Run backend
python wsgi.py

# Terminal 2 - Run frontend
cd frontend
npm start
```

## Environment Variables

Create a `.env` file in the root directory with the following variables (or use generate_env.py):
```
FLASK_APP=app.py
FLASK_ENV=development
NODE_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/filmila_db
JWT_SECRET_KEY=your_jwt_secret_key
SECRET_KEY=your_secret_key
STRIPE_SECRET_KEY=your_stripe_secret_key
FRONTEND_URL=http://localhost:3000
PORT=8080
```

## Database Models

The application uses SQLAlchemy ORM with the following models:

### User Model
- id: Primary key
- username: Unique username
- email: Unique email address
- password_hash: Securely hashed password
- is_filmmaker: Boolean flag for filmmaker status

### Film Model
- id: Primary key
- title: Film title
- description: Film description
- price: Film price in cents
- filmmaker_id: Foreign key to User model
- upload_date: Timestamp of upload

### Purchase Model
- id: Primary key
- user_id: Foreign key to User model
- film_id: Foreign key to Film model
- purchase_date: Timestamp of purchase
- payment_id: Stripe payment ID

## API Endpoints

- `GET /api/films` - Get all films
- `POST /api/upload` - Upload a new film (requires filmmaker authentication)
- `POST /api/create-payment-intent` - Create a payment intent for film purchase
- `GET /api/watch/<film_id>` - Stream a purchased film

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
