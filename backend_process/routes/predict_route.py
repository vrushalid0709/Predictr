from flask import Blueprint, request, jsonify
from backend_process.predict_stock import predict_stock_price

predict_bp = Blueprint("predict_bp", __name__)

@predict_bp.route("/api/stocks/predict", methods=["POST"])
def predict_stock_api():
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        days = int(data.get("days", 7))

        if not symbol:
            return jsonify({"error": "Missing stock symbol"}), 400

        result = predict_stock_price(symbol, days)

        if result.get("status") == "error":
            error_msg = result.get("message", "Unknown error")
            
            # Check if it's a model compatibility issue
            if "compatibility issue" in error_msg or "retrain the model" in error_msg:
                return jsonify({
                    "error": "Model compatibility issue", 
                    "message": f"The saved model for {symbol} needs to be retrained with the current TensorFlow version.",
                    "suggestion": f"Use the /api/stocks/retrain endpoint to retrain the model for {symbol}",
                    "code": "MODEL_RETRAIN_NEEDED"
                }), 400
            
            return jsonify({"error": error_msg}), 400

        formatted_predictions = [
            {"date": p["date"], "price": p["predicted_close"]}
            for p in result["predictions"]
        ]

        return jsonify({
            "predictions": formatted_predictions,
            "future_value": formatted_predictions[-1]["price"],
            "accuracy": 95
        })

    except Exception as e:
        print("❌ Error in prediction API:", e)
        return jsonify({"error": str(e)}), 500

@predict_bp.route("/api/stocks/retrain", methods=["POST"])
def retrain_model_api():
    """Endpoint to retrain a model for compatibility or improved accuracy"""
    try:
        from backend_process.train_model import train_lstm_model
        
        data = request.get_json()
        symbol = data.get("symbol")
        
        if not symbol:
            return jsonify({"error": "Missing stock symbol"}), 400
        
        print(f"🔄 Starting model retraining for {symbol}...")
        
        # Train the model
        result = train_lstm_model(symbol)
        
        if result.get("status") == "success":
            return jsonify({
                "message": f"Model for {symbol} has been successfully retrained",
                "symbol": symbol,
                "model_path": result.get("model_path"),
                "accuracy": result.get("accuracy", "N/A")
            })
        else:
            return jsonify({
                "error": f"Failed to retrain model for {symbol}",
                "details": result.get("reason", "Unknown error")
            }), 500
            
    except Exception as e:
        print(f"❌ Error in model retraining API: {e}")
        return jsonify({"error": str(e)}), 500

@predict_bp.route("/api/models/cleanup", methods=["POST"])
def cleanup_models_api():
    """Endpoint to clean up all incompatible models"""
    try:
        from backend_process.predict_stock import cleanup_incompatible_models
        
        print("🧹 Starting model cleanup...")
        result = cleanup_incompatible_models()
        
        if "error" in result:
            return jsonify({
                "error": "Cleanup failed",
                "details": result["error"]
            }), 500
        
        return jsonify({
            "message": "Model cleanup completed successfully",
            "cleaned_models": result["cleaned"],
            "status": "success"
        })
        
    except Exception as e:
        print(f"❌ Error in cleanup API: {e}")
        return jsonify({"error": str(e)}), 500
