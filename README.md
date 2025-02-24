# Filmila - Independent Filmmaker Platform

A platform for independent filmmakers to share their work and monetize their content through pay-per-view streaming.

## Features

- Film upload for creators
- Pay-per-view system
- Secure payment processing with Stripe
- Beautiful gallery-style homepage
- Film categorization
- User authentication for both filmmakers and viewers

## Project Structure

```
filmila-webapp/
├── app.py                 # Flask backend
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

1. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set STRIPE_SECRET_KEY=your_stripe_secret_key
set SECRET_KEY=your_secret_key
```

2. Set up the frontend:
```bash
cd frontend
npm install
```

3. Run the application:
```bash
# Terminal 1 - Run backend
flask run

# Terminal 2 - Run frontend
cd frontend
npm start
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

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
