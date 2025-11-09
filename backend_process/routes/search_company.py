
from flask import Blueprint, request, jsonify
import requests

fetch_stock = Blueprint("fetch_stock", __name__)

@fetch_stock.route("/search_company", methods=["GET"])
def search_company():
    # 1️⃣ Get the company name or keyword from the URL
    company = request.args.get("company")
    if not company:
        return jsonify({"error": "No company provided"}), 400

    try:
        # Yahoo search API URL
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company}"

        # FLASK request as normal browser
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/116.0.0.0 Safari/537.36"
            )
        }

        # Yahoo request
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()  # raise error if request failed

        # JSON conversion
        data = res.json()

        # extracting result 
        results = data.get("quotes", [])
        if not results:
            return jsonify({"error": "No matches found"}), 404

        # small list of info
        out = []
        for r in results:
            out.append({
                "symbol": r.get("symbol"),
                "shortname": r.get("shortname"),
                "exchange": r.get("exchange"),
                "currency": r.get("currency")
            })

        # returns in json format
        return jsonify({"results": out})
    
    except requests.exceptions.RequestException as e:
        # Handles connection issues, timeouts, etc.
        print("Yahoo request failed:", e)
        return jsonify({"error": "Yahoo request failed"}), 500
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
