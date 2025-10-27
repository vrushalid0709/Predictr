
from flask import Blueprint, request, jsonify
import yfinance as yf  # Yahoo Finance Python package 

fetch_stock = Blueprint("fetch_stock", __name__)

@fetch_stock.route("/api/fetch_stock_details", methods=["GET"])
def fetch_stock_details():
    # Get the stock symbol 
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Missing symbol"}), 400  #error if none

    try:
        # creating stock object using yfinance
        stock = yf.Ticker(symbol)

        # storing stock info in dict
        info = stock.info

        # error return 
        if not info:
            return jsonify({"error": "No data found"}), 404

        # details extracted from dict 
        data = {
            "symbol": symbol,
            "longName": info.get("longName"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
            "sector": info.get("sector"),
            "currentPrice": info.get("currentPrice")
        }

        # sent to website in JSON format
        return jsonify(data)

    except Exception as e:
        # exception if data fetching fails 
        return jsonify({"error": str(e)}), 500
