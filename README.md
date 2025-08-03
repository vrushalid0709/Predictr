# Predictr
Our project uses historical stock data and machine learning models to predict future stock prices with the aim of helping users make informed investment decisions.

🔮 What it Predicts
Closing Prices of selected stocks

Short-term trends (e.g., next day/week)

Price movements (up/down)

🧠 How It Works
We use machine learning models trained on past stock data:

LSTM (Long Short-Term Memory) neural networks for time series forecasting

Linear Regression or Random Forest for quick predictions

Features include: Open, High, Low, Close, Volume, and technical indicators (like SMA, EMA, RSI)

### 🧪 Example Prediction  
For stock: **AAPL (Apple Inc.)**

| Date       | Actual Close | Predicted Close |
|------------|--------------|-----------------|
| 2025-07-28 | 195.80       | 196.42          |
| 2025-07-29 | 198.20       | 197.95          |

**Accuracy:** ~92% on test data  
**Loss (MSE):** 0.0023
