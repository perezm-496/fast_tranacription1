import requests

BASE_URL = "http://localhost:8000/elise"

# User info
user_data = {
    "name": "Alice",
    "surename": "Wonderland",
    "email": "alice@example.com",
    "phone_number": "1234567890",
    "password": "securepass123"
}

# Step 1: Create User
response = requests.post(f"{BASE_URL}/users/", json=user_data)
if response.status_code != 200:
    print("Failed to create user:", response.json())
    exit(1)

user_id = response.json()["id"]
print("✅ User created:", user_id)

# Step 2: Create Membership
membership_data = {
    "user_id": user_id,
    "type": "Testing",
    "available": 10 * 100
}

response = requests.post(f"{BASE_URL}/memberships/", json=membership_data)
if response.status_code != 200:
    print("Failed to create membership:", response.json())
    exit(1)

print("✅ Membership created:", response.json())
