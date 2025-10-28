#StockRoutes.py code
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from db_connection.db import db
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend_process.utils.stock_helpers import user_stocks_helper
from backend_process.utils.user_helpers import user_helper

stock_routes = Blueprint("stock_routes", __name__)

print("✅ StockRoutes blueprint loaded successfully")


# ===== Add a Stock =====
@stock_routes.route("/stocks/add_stock", methods=["POST"])
def add_stock():
    data = request.get_json()
    
    # Try to get user_id from multiple sources
    user_id = session.get("user_id") or data.get("user_id")
    
    # If no user_id, try to get it from email in session
    if not user_id and session.get("user"):
        user_email = session.get("user")
        user_id = user_helper.get_user_id_by_email(user_email)
        if user_id:
            # Update session with user_id for future requests
            session["user_id"] = user_id
            print(f"🔄 Retrieved user_id {user_id} for email {user_email}")

    if not user_id:
        return jsonify({"error": "Missing user_id - please log in"}), 401

    # Use the UserStocks helper to add stock
    result = user_stocks_helper.add_stock(user_id, data)
    
    if result["success"]:
        # Convert ObjectId to string to make it JSON serializable
        stock_data = result.get("data", {})
        if "_id" in stock_data:
            stock_data["_id"] = str(stock_data["_id"])
        
        return jsonify({
            "message": result["message"], 
            "stock": stock_data
        }), 201 if "added successfully" in result["message"] else 200
    else:
        return jsonify({"error": result["error"]}), 400

# ===== Get All Stocks for a User =====
@stock_routes.route("/stocks/get_stocks", methods=["GET"])
def get_stocks():
    # Try to get user_id from multiple sources
    user_id = session.get("user_id") or request.args.get("user_id")
    
    # If no user_id, try to get it from email in session
    if not user_id and session.get("user"):
        user_email = session.get("user")
        user_id = user_helper.get_user_id_by_email(user_email)
        if user_id:
            # Update session with user_id for future requests
            session["user_id"] = user_id
            print(f"🔄 Retrieved user_id {user_id} for email {user_email}")

    if not user_id:
        return jsonify({"error": "Missing user_id - please log in"}), 401

    # Use the UserStocks helper to get stocks
    result = user_stocks_helper.get_user_stocks(user_id)
    
    if result["success"]:
        return jsonify({
            "stocks": result["stocks"],
            "count": result["count"]
        }), 200
    else:
        return jsonify({"error": result["error"]}), 500

# ===== Update a Stock =====
@stock_routes.route("/stocks/update_stock", methods=["PUT"])
def update_stock():
    data = request.get_json()
    
    # Try to get user_id from multiple sources
    user_id = session.get("user_id") or data.get("user_id")
    
    # If no user_id, try to get it from email in session
    if not user_id and session.get("user"):
        user_email = session.get("user")
        user_id = user_helper.get_user_id_by_email(user_email)
        if user_id:
            session["user_id"] = user_id
    
    symbol = data.get("symbol")

    if not user_id or not symbol:
        return jsonify({"error": "Missing user_id or symbol - please log in"}), 401

    # Use the UserStocks helper to update stock
    result = user_stocks_helper.update_stock(user_id, symbol, data)
    
    if result["success"]:
        return jsonify({
            "message": result["message"], 
            "stock": result.get("data")
        }), 200
    else:
        return jsonify({"error": result["error"]}), 400

# ===== Remove a Stock =====
@stock_routes.route("/stocks/remove_stock", methods=["POST", "DELETE"])
def remove_stock():
    data = request.get_json()
    
    # Try to get user_id from multiple sources
    user_id = session.get("user_id") or data.get("user_id")
    
    # If no user_id, try to get it from email in session
    if not user_id and session.get("user"):
        user_email = session.get("user")
        user_id = user_helper.get_user_id_by_email(user_email)
        if user_id:
            session["user_id"] = user_id
    
    symbol = data.get("symbol")

    if not user_id or not symbol:
        return jsonify({"error": "Missing user_id or symbol - please log in"}), 401

    # Use the UserStocks helper to remove stock
    result = user_stocks_helper.remove_stock(user_id, symbol)
    
    if result["success"]:
        return jsonify({"message": result["message"]}), 200
    else:
        return jsonify({"error": result["error"]}), 400


# ===== Get Stock Price (Real-time) =====
@stock_routes.route("/stocks/get_stock_price", methods=["POST"])
def get_stock_price():
    """Fetch current stock price and basic info for a given symbol"""
    try:
        data = request.get_json()
        symbol = data.get("symbol", "").strip().upper()
        
        if not symbol:
            return jsonify({"error": "Symbol is required"}), 400
        
        # Import yfinance here to avoid loading it if not needed
        try:
            import yfinance as yf
        except ImportError:
            return jsonify({"error": "yfinance not installed"}), 500
        
        # Fetch stock data
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        if hist.empty or not info:
            return jsonify({"error": f"No data found for symbol {symbol}"}), 404
        
        # Get current price (most recent close)
        current_price = hist['Close'].iloc[-1] if not hist.empty else None
        
        if current_price is None:
            return jsonify({"error": f"Unable to fetch current price for {symbol}"}), 404
        
        # Extract useful information
        stock_data = {
            "symbol": symbol,
            "currentPrice": round(float(current_price), 2),
            "longName": info.get("longName", ""),
            "exchange": info.get("exchange", ""),
            "currency": info.get("currency", "USD"),
            "sector": info.get("sector", ""),
            "previousClose": info.get("previousClose"),
            "marketCap": info.get("marketCap"),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📈 Fetched price for {symbol}: ${current_price}")
        return jsonify(stock_data), 200
        
    except Exception as e:
        print(f"❌ Error fetching stock price: {str(e)}")
        return jsonify({"error": f"Failed to fetch stock price: {str(e)}"}), 500


# ===== Get Live Exchange Rates =====
@stock_routes.route("/exchange-rates", methods=["GET"])
def get_exchange_rates():
    """Fetch live exchange rates from ExchangeRate-API"""
    try:
        import requests
        import os
        
        # Get API key from environment variable
        api_key = os.getenv('EXCHANGE_RATE_API_KEY')
        
        if not api_key:
            print("⚠️ EXCHANGE_RATE_API_KEY not found in environment, using default rates")
            # Return default rates if no API key
            return jsonify({
                "rates": {
                    "USD": 1,
                    "EUR": 0.92,
                    "GBP": 0.78,
                    "INR": 84
                },
                "timestamp": datetime.now().isoformat(),
                "source": "default"
            }), 200
        
        # Fetch from ExchangeRate-API
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("result") == "success":
                print("✅ Successfully fetched live exchange rates")
                return jsonify({
                    "rates": data.get("conversion_rates", {}),
                    "timestamp": data.get("time_last_update_utc"),
                    "source": "exchangerate-api.com"
                }), 200
            else:
                print(f"❌ ExchangeRate-API error: {data.get('error-type')}")
                raise Exception(f"API returned error: {data.get('error-type')}")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error fetching exchange rates: {str(e)}")
        # Return default rates on error
        return jsonify({
            "rates": {
                "USD": 1,
                "EUR": 0.92,
                "GBP": 0.78,
                "INR": 84
            },
            "timestamp": datetime.now().isoformat(),
            "source": "default (error)",
            "error": str(e)
        }), 200  # Return 200 with default rates instead of error