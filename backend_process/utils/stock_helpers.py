# stock_helpers.py - Utility functions for UserStocks collection operations
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db_connection.db import db
from flask import request

class UserStocksHelper:
    """Helper class for managing user stocks in MongoDB UserStocks collection"""
    
    def __init__(self):
        self.collection = db.UserStocks  # New collection for user stocks
    
    def add_stock(self, user_id: str, stock_data: Dict) -> Dict:
        """
        Add a new stock to user's portfolio
        
        Args:
            user_id: User identifier
            stock_data: Dictionary containing stock information
            
        Returns:
            Dictionary with result status and data
        """
        try:
            # Validate required fields
            if not user_id or not stock_data.get('symbol'):
                return {"error": "Missing required fields: user_id and symbol", "success": False}
            
            symbol = stock_data.get('symbol').upper()
            
            # Check if stock already exists for this user
            existing = self.collection.find_one({
                "user_id": user_id, 
                "symbol": symbol
            })
            
            if existing:
                # Update existing stock instead of just returning it
                print(f"🔄 Stock {symbol} already exists, updating with new data...")
                update_result = self.update_stock(user_id, symbol, stock_data)
                if update_result["success"]:
                    return {"message": "Stock updated successfully", "success": True, "data": update_result["data"]}
                else:
                    return update_result
            
            # Prepare stock document
            stock_document = {
                "user_id": user_id,
                "symbol": symbol,
                "name": stock_data.get("longName") or stock_data.get("company") or stock_data.get("name") or "",
                "exchange": stock_data.get("exchange") or "",
                "currency": stock_data.get("currency") or "USD",
                "sector": stock_data.get("sector") or "",
                "qty": self._safe_int(stock_data.get("qty")),
                "buy_price": self._safe_float(stock_data.get("buy") or stock_data.get("buy_price") or stock_data.get("buyPrice")),
                "current_price": self._safe_float(stock_data.get("current") or stock_data.get("currentPrice") or stock_data.get("current_price")),
                "date": stock_data.get("date") or datetime.utcnow().strftime("%Y-%m-%d"),
                "ip_address": request.remote_addr if request else "unknown",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into UserStocks collection
            result = self.collection.insert_one(stock_document)
            stock_document['_id'] = str(result.inserted_id)
            
            print(f"✅ Stock added to UserStocks collection - User: {user_id}, Symbol: {symbol}")
            
            return {
                "message": "Stock added successfully to UserStocks",
                "success": True,
                "data": stock_document
            }
            
        except Exception as e:
            print(f"❌ Error adding stock to UserStocks: {str(e)}")
            return {"error": f"Failed to add stock: {str(e)}", "success": False}
    
    def get_user_stocks(self, user_id: str) -> Dict:
        """
        Retrieve all stocks for a specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with stocks list and status
        """
        try:
            if not user_id:
                return {"error": "Missing user_id", "success": False}
            
            # Fetch all stocks for user from UserStocks collection
            stocks_cursor = self.collection.find(
                {"user_id": user_id},
                {"_id": 0}  # Exclude MongoDB _id field
            ).sort("created_at", -1)  # Sort by newest first
            
            stocks = list(stocks_cursor)
            
            print(f"📊 Retrieved {len(stocks)} stocks for user {user_id} from UserStocks collection")
            
            return {
                "stocks": stocks,
                "count": len(stocks),
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error fetching user stocks: {str(e)}")
            return {"error": f"Failed to fetch stocks: {str(e)}", "success": False}
    
    def update_stock(self, user_id: str, symbol: str, update_data: Dict) -> Dict:
        """
        Update an existing stock in user's portfolio
        
        Args:
            user_id: User identifier
            symbol: Stock symbol to update
            update_data: Dictionary with fields to update
            
        Returns:
            Dictionary with result status and data
        """
        try:
            if not user_id or not symbol:
                return {"error": "Missing user_id or symbol", "success": False}
            
            # Prepare update document
            update_doc = {"updated_at": datetime.utcnow()}
            
            # Add fields that are provided (handle multiple field name variations)
            if "qty" in update_data:
                update_doc["qty"] = self._safe_int(update_data["qty"])
            if any(key in update_data for key in ["buy_price", "buy", "buyPrice"]):
                update_doc["buy_price"] = self._safe_float(update_data.get("buy_price") or update_data.get("buy") or update_data.get("buyPrice"))
            if any(key in update_data for key in ["current_price", "current", "currentPrice"]):
                update_doc["current_price"] = self._safe_float(update_data.get("current_price") or update_data.get("current") or update_data.get("currentPrice"))
            if "date" in update_data:
                update_doc["date"] = update_data["date"]
            
            # Also update company name and other info if provided
            if any(key in update_data for key in ["longName", "company", "name"]):
                update_doc["name"] = update_data.get("longName") or update_data.get("company") or update_data.get("name")
            if "currency" in update_data:
                update_doc["currency"] = update_data.get("currency")
            if "exchange" in update_data:
                update_doc["exchange"] = update_data.get("exchange")
            if "sector" in update_data:
                update_doc["sector"] = update_data.get("sector")
            
            # Update the stock
            result = self.collection.update_one(
                {"user_id": user_id, "symbol": symbol.upper()},
                {"$set": update_doc}
            )
            
            if result.matched_count == 0:
                return {"error": "Stock not found", "success": False}
            
            # Get updated document
            updated_stock = self.collection.find_one(
                {"user_id": user_id, "symbol": symbol.upper()},
                {"_id": 0}
            )
            
            print(f"📝 Stock updated in UserStocks - User: {user_id}, Symbol: {symbol}")
            
            return {
                "message": "Stock updated successfully",
                "success": True,
                "data": updated_stock
            }
            
        except Exception as e:
            print(f"❌ Error updating stock: {str(e)}")
            return {"error": f"Failed to update stock: {str(e)}", "success": False}
    
    def remove_stock(self, user_id: str, symbol: str) -> Dict:
        """
        Remove a stock from user's portfolio
        
        Args:
            user_id: User identifier
            symbol: Stock symbol to remove
            
        Returns:
            Dictionary with result status
        """
        try:
            if not user_id or not symbol:
                return {"error": "Missing user_id or symbol", "success": False}
            
            result = self.collection.delete_one({
                "user_id": user_id,
                "symbol": symbol.upper()
            })
            
            if result.deleted_count == 0:
                return {"error": "Stock not found", "success": False}
            
            print(f"🗑️ Stock removed from UserStocks - User: {user_id}, Symbol: {symbol}")
            
            return {
                "message": "Stock removed successfully",
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error removing stock: {str(e)}")
            return {"error": f"Failed to remove stock: {str(e)}", "success": False}
    
    def get_stock_count(self, user_id: str) -> int:
        """Get total count of stocks for a user"""
        try:
            return self.collection.count_documents({"user_id": user_id})
        except Exception:
            return 0
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None or value == '':
            return None
        try:
            return int(float(value))  # Handle string numbers
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

# Create singleton instance
user_stocks_helper = UserStocksHelper()