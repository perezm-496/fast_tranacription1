import requests

from pymongo import MongoClient
from bson import ObjectId
import bcrypt

# Connect to MongoDB
client = MongoClient(
    "mongodb://elise:elise_can_open_doors@localhost:27017/elise_db?authSource=admin"
)
db = client.elise_db

# User info
user_data = {
    "name": "Andrea", 
    "surename": "Lara",
    "email": "andrea@healthailabs.com",
    "phone_number": "+52 55 5555 5555",
    "password": bcrypt.hashpw("¿Cuál es su pass?".encode(), bcrypt.gensalt())
}

# Step 1: Create User
result = db.users.insert_one(user_data)
user_id = str(result.inserted_id)
print("✅ User created:", user_id)

# Step 2: Create Membership
membership_data = {
    "user_id": ObjectId(user_id),
    "type": "Testing",
    "available": 10 * 100
}

result = db.memberships.insert_one(membership_data)
print("✅ Membership created:", str(result.inserted_id))
