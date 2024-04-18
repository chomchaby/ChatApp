from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash
from user import User
import os

mongo_uri = os.getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

chat_db = client.get_database('chat-db')
users_collection = chat_db.get_collection("users")

def save_user(username, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id':username, 'password':password_hash})

def get_user(username):
    user_data = users_collection.find_one({'_id':username})
    return User(user_data['_id'], user_data['password']) if user_data else None