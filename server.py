import os
from waitress import serve

# Set environment variables directly
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'
os.environ['NODE_ENV'] = 'development'
os.environ['JWT_SECRET_KEY'] = 'eMFnC2rzQ7ErqlXl6vpSqpG3c81oCNC69q96Q+vxcv8='
os.environ['FRONTEND_URL'] = 'http://localhost:3000'
os.environ['REACT_APP_API_URL'] = 'http://localhost:8080/api'
os.environ['PORT'] = '8080'

# Import app after setting environment variables
from app import app
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"Starting server on port {port} in {os.getenv('FLASK_ENV')} mode...")
    if os.getenv('FLASK_ENV') == 'development':
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        serve(app, host='0.0.0.0', port=port, threads=6)
