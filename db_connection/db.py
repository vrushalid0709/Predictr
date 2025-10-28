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

# Initialize collections
try:
    # Ensure UserStocks collection exists with proper indexing
    if "UserStocks" not in db.list_collection_names():
        db.create_collection("UserStocks")
        print("✅ UserStocks collection created")
    
    # Create indexes for better performance
    db.UserStocks.create_index([("user_id", 1), ("symbol", 1)], unique=True)
    db.UserStocks.create_index([("user_id", 1)])
    db.UserStocks.create_index([("created_at", -1)])
    
    print("✅ Database and UserStocks collection initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize UserStocks collection: {e}")
    print("   Collection will be created automatically when first document is inserted")
