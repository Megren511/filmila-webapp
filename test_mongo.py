from pymongo import MongoClient
from pymongo.server_api import ServerApi
import sys

uri = "mongodb+srv://megrenfilms:MV52eUzhYOxRHavW@cluster0.jlezl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # List all databases
    print("\nAvailable databases:")
    for db in client.list_database_names():
        print(f"- {db}")
        
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    sys.exit(1)
finally:
    client.close()
