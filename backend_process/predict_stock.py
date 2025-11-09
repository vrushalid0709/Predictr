

import os
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model
from dotenv import load_dotenv
import json
from pymongo import MongoClient

#  Load environment variables

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("MODEL_COLLECTION", "trained_models")

# Connect to MongoDB

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# Predict future stock prices

def predict_stock_price(stock_symbol, days_to_predict=5):
    print(f"\n Generating predictions for {stock_symbol}...")

    # Find model info in MongoDB
    record = collection.find_one({"stock_symbol": stock_symbol})
    if not record:
        return {"status": "error", "message": "Model not found for this stock!"}

    model_path = record["model_path"]
    
    # === Load the saved scaler values ===
    scaler_min = record.get("scaler_min")
    scaler_max = record.get("scaler_max")
    
    if scaler_min is None or scaler_max is None:
        return {"status": "error", "message": "Model record is missing scaler min/max values!"}

    if not os.path.exists(model_path):
        return {"status": "error", "message": f"Model file missing: {model_path}"}

    # Load trained model
    model = load_model(model_path)

    # Fetch recent 60 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=120) # Fetch more to ensure we have 60 trading days
    data = yf.download(stock_symbol, start=start_date, end=end_date)

    if data.empty:
        return {"status": "error", "message": "No data available from yfinance."}

    close_prices = data["Close"].values.reshape(-1, 1)

    
    scaled_data = (close_prices - scaler_min) / (scaler_max - scaler_min)

    if len(scaled_data) < 60:
        return {"status": "error", "message": f"Not enough historical data; need 60 days, got {len(scaled_data)}"}
        
    last_60_days = scaled_data[-60:]
    predictions = []

    current_input = last_60_days.copy()

    # Predict next n days
    for _ in range(days_to_predict):
        X_test = np.reshape(current_input, (1, current_input.shape[0], 1))
        pred_price = model.predict(X_test, verbose=0)
        predictions.append(pred_price[0][0])

        # Append the new predicted value and remove the oldest
        current_input = np.append(current_input[1:], pred_price)
        current_input = np.reshape(current_input, (60, 1))

    #  Manually inverse transform using the *loaded* min/max 
    scaled_predictions = np.array(predictions).reshape(-1, 1)
    predicted_prices = (scaled_predictions * (scaler_max - scaler_min)) + scaler_min
    predicted_prices = predicted_prices.flatten().tolist()


    # Create date range for predictions
    prediction_dates = [(end_date + timedelta(days=i+1)).strftime("%Y-%m-%d") for i in range(days_to_predict)]

    # Combine into results
    results = {
        "status": "success",
        "stock_symbol": stock_symbol,
        "predictions": [
            {"date": prediction_dates[i], "predicted_close": round(predicted_prices[i], 2)}
            for i in range(days_to_predict)
        ]
    }

    # Print or return JSON result
    print(f"\n Prediction completed for {stock_symbol}:\n{json.dumps(results, indent=4)}\n")
    return {
    "status": results["status"],
    "stock_symbol": results["stock_symbol"],
    "predictions": results["predictions"]
}



# Run manually for testing
if __name__ == "__main__":
    stock_symbol = input("Enter stock symbol (e.g. AAPL, TSLA): ").upper()
    result = predict_stock_price(stock_symbol)