# user_helpers.py - Utility functions for user operations
from typing import Optional, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db_connection.db import db

def generate_user_id():
    counters = db['counters']
    counter_doc = counters.find_one_and_update(
        {"_id": "user_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return f"USR-{counter_doc['seq']}"

class UserHelper:
    """Helper class for managing user operations"""
    
    def __init__(self):
        self.collection = db.users  # Users collection
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user document by email
        
        Args:
            email: User's email address
            
        Returns:
            User document or None if not found
        """
        try:
            if not email:
                return None
            
            user = self.collection.find_one({"email": email.lower().strip()})
            return user
            
        except Exception as e:
            print(f"❌ Error fetching user by email: {str(e)}")
            return None
    
    def get_user_id_by_email(self, email: str) -> Optional[str]:
        """
        Get user_id (MongoDB ObjectId as string) by email
        
        Args:
            email: User's email address
            
        Returns:
            User ID as string or None if not found
        """
        try:
            user = self.get_user_by_email(email)
            if user and '_id' in user:
                return str(user['_id'])
            return None
            
        except Exception as e:
            print(f"❌ Error getting user_id by email: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user document by user_id
        
        Args:
            user_id: User's ObjectId as string
            
        Returns:
            User document or None if not found
        """
        try:
            from bson import ObjectId
            
            if not user_id:
                return None
            
            # Convert string to ObjectId
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            return user
            
        except Exception as e:
            print(f"❌ Error fetching user by ID: {str(e)}")
            return None
    
    def validate_user_session(self, session) -> Dict:
        """
        Validate user session and return user info
        
        Args:
            session: Flask session object
            
        Returns:
            Dictionary with user_id, email, name and validation status
        """
        try:
            user_email = session.get('user')
            if not user_email:
                return {"valid": False, "error": "No user in session"}
            
            user = self.get_user_by_email(user_email)
            if not user:
                return {"valid": False, "error": "User not found in database"}
            
            return {
                "valid": True,
                "user_id": str(user['_id']),
                "email": user['email'],
                "name": user.get('name', 'User')
            }
            
        except Exception as e:
            print(f"❌ Error validating user session: {str(e)}")
            return {"valid": False, "error": str(e)}

# Create singleton instance
user_helper = UserHelper()
