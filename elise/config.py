from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://elise:elise_can_open_doors@mongo:27017/elise_db?authSource=elise_db")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "elise_db")
ROOT_PATH = os.getenv("ROOT_PATH", "/")
