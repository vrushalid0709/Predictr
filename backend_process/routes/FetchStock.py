from flask import Blueprint, request, jsonify
import yfinance as yf
import requests

fetch_stock = Blueprint("fetch_stock", __name__)

@fetch_stock.route("/fetch_stock_details", methods=["GET"])
def fetch_stock_details():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Missing symbol"}), 400
    
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info:
            return jsonify({"error": "No data found"}), 404

        return jsonify({
            "symbol": symbol,
            "longName": info.get("longName"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
            "sector": info.get("sector"),
            "currentPrice": info.get("currentPrice")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fetch_stock.route("/search_company", methods=["GET"])
def search_company():
    company = request.args.get("company")
    if not company:
        return jsonify({"error": "No company provided"}), 400

    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company}"
        headers = {
                  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0.0.0 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()  # Raises HTTPError if status != 200

        data = res.json()
        results = data.get("quotes", [])
        if not results:
            return jsonify({"error": "No matches found"}), 404

        out = []
        for r in results:
            out.append({
                "symbol": r.get("symbol"),
                "shortname": r.get("shortname"),
                "exchange": r.get("exchange"),
                "currency": r.get("currency")
            })

        return jsonify({"results": out})
    
    except requests.exceptions.RequestException as e:
        print("Yahoo request failed:", e)
        return jsonify({"error": "Yahoo request failed"}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

