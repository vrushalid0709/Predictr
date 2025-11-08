# ===============================
# Predictr - Stock Model Trainer (with .env)
# ===============================

import os
import numpy as np
import yfinance as yf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from pymongo import MongoClient
from dotenv import load_dotenv
import json


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# Fetch MongoDB connection details
MONGO_URI = os.getenv("MONGO_URI")     
DB_NAME = os.getenv("DB_NAME")         
COLLECTION_NAME = os.getenv("MODEL_COLLECTION", "trained_models")

# Check if environment variables loaded
if not MONGO_URI or not DB_NAME:
    raise ValueError("MongoDB connection details not found in .env file!")

#  MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# Function: Train LSTM Model
def train_lstm_model(stock_symbol, epochs=50, time_steps=60):
    print(f"\n Training started for {stock_symbol}...")

    # Fetch historical stock data
    data = yf.download(stock_symbol, start="2020-01-01", end=datetime.now().strftime("%Y-%m-%d"))

    if data.empty:
        print(f" No data found for {stock_symbol}.")
        return {"status": "failed", "reason": "No stock data"}

    # Use only closing prices
    close_prices = data['Close'].values.reshape(-1, 1)

    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(close_prices)

    # Create training sequences
    X_train, y_train = [], []
    for i in range(time_steps, len(scaled_data)):
        X_train.append(scaled_data[i - time_steps:i, 0])
        y_train.append(scaled_data[i, 0])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    
    #Build the LSTM Model
    
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Add early stopping to prevent overfitting
    early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)

   
    # Train the Model
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=32, callbacks=[early_stop], verbose=1)

   
    # Save Model 
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{stock_symbol}_lstm.h5")
    model.save(model_path)

    # Store training details in MongoDB
    model_record = {
        "stock_symbol": stock_symbol,
        "trained_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "epochs": len(history.history["loss"]),
        "model_path": model_path,
        "scaler_min": float(scaler.data_min_[0]),
        "scaler_max": float(scaler.data_max_[0]),
    }
    collection.insert_one(model_record)

    print(f" Model trained and saved: {model_path}")
    return {"status": "success", "model_path": model_path, "trained_epochs": len(history.history['loss'])}



# 7. Run Directly (Manual Train)
if __name__ == "__main__":
    stock_symbol = input("Enter stock symbol (e.g. AAPL, TSLA): ").upper()
    result = train_lstm_model(stock_symbol)
    print(json.dumps(result, indent=4))
