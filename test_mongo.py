# from pymongo import MongoClient
# from datetime import datetime

# # Connection URI
# uri = "mongodb://elise:elise_can_open_doors@mongo:27017/elise_db?authSource=elise_db"

# # Connect to MongoDB
# client = MongoClient(uri)

# # Select database and collection
# db = client['elise_db']
# collection = db['test']  # or any collection you want

# # Create and insert the document
# doc = {
#     'action': 'test',
#     'result': 'success',
#     'date': datetime.utcnow()  # Use datetime.now() if you want local time
# }

# insert_result = collection.insert_one(doc)

# # Print confirmation
# print("Inserted with ID:", insert_result.inserted_id)

from pymongo import MongoClient

uri = "mongodb://elise:elise_can_open_doors@mongo:27017/elise_db?authSource=elise_db"
client = MongoClient(uri)

print(client.list_database_names())
