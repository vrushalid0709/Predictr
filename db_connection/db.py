# db_connection/db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise RuntimeError("The 'MONGO_URI' environment variable is not set.")

client = MongoClient(mongo_uri)
db = client["predictr_db"]
