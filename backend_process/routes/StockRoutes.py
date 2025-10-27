#StockRoutes.py code
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from db_connection.db import db

stock_routes = Blueprint("stock_routes", __name__)

print("✅ StockRoutes blueprint loaded successfully")


# ===== Add a Stock =====
@stock_routes.route("/stocks/add_stock", methods=["POST"])
def add_stock():
    data = request.get_json()
    user_id = session.get("user_id") or data.get("user_id")
    symbol = data.get("symbol")

    if not all([user_id, symbol]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Check if already saved
        existing = db.user_stocks.find_one({"user_id": user_id, "symbol": symbol})
        if existing:
            return jsonify({"message": "Stock already saved"}), 200

        stock_entry = {
            "user_id": user_id,
            "symbol": symbol,
            "longName": data.get("longName"),
            "exchange": data.get("exchange"),
            "currency": data.get("currency"),
            "sector": data.get("sector"),
            "currentPrice": data.get("currentPrice"),
            "saved_at": datetime.utcnow()
        }

        db.user_stocks.insert_one(stock_entry)
        print(f" Saved stock for user {user_id}: {symbol}")

        return jsonify({"message": "Stock added successfully", "stock": stock_entry}), 201

    except Exception as e:
        print(f" Error while saving stock: {e}")
        return jsonify({"error": str(e)}), 500

# ===== Get All Stocks for a User =====
@stock_routes.route("/stocks/get_stocks", methods=["GET"])
def get_stocks():
    user_id = session.get("user_id") or request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        stocks = list(db.user_stocks.find({"user_id": user_id}, {"_id": 0}))
        return jsonify({"stocks": stocks}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500