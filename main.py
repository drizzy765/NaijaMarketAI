from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
import os


# 1. INITIALIZE APP

app = FastAPI(
    title="🇳🇬 AgroPulse API",
    description="Multi-Commodity Food Price Prediction & History Server",
    version="2.0"
)

# 2. LOAD RESOURCES (MODELS & DATA)


# A. Load the "Mega-Brain" (All Trained Models)
model_path = "all_models.pkl"
if os.path.exists(model_path):
    with open(model_path, "rb") as f:
        model_warehouse = pickle.load(f)
    print(f" Loaded AI Models for: {list(model_warehouse.keys())}")
else:
    print(" WARNING: 'all_models.pkl' not found. Predictions will fail.")
    model_warehouse = {}

# B. Load Historical Data (For the Frontend Charts)
history_path = "final_dataset_cleaned_v3.csv"
if os.path.exists(history_path):
    try:
        history_df = pd.read_csv(history_path)
        history_df['date'] = pd.to_datetime(history_df['date'])
        print(f" Loaded Historical Data: {len(history_df)} rows")
    except Exception as e:
        print(f" Error loading history CSV: {e}")
        history_df = pd.DataFrame()
else:
    print("WARNING: 'final_dataset_cleaned_v3.csv' not found. Charts will be empty.")
    history_df = pd.DataFrame()


# 3. DEFINE INPUT FORMAT

class MarketData(BaseModel):
    item_id: str          # e.g., 'rice_local'
    current_price: float  # e.g., 50000
    fuel_price: float     # e.g., 1000
    diesel_price: float   # e.g., 1200


# 4. ENDPOINTS


@app.get("/")
def home():
    """Health Check"""
    return {
        "status": "Online",
        "models_available": list(model_warehouse.keys()),
        "history_data_available": not history_df.empty
    }

@app.get("/history/{item_id}")
def get_item_history(item_id: str):
    """
    Returns the last 90 days of price history for a specific item.
    Used by the Frontend to draw the line chart.
    """
    if history_df.empty:
        return {"error": "No historical data available on server."}
    
    # Filter for the specific item
    subset = history_df[history_df['item_id'] == item_id]
    
    if subset.empty:
        return {"dates": [], "prices": []}
    
    # Sort and take the last 90 days
    subset = subset.sort_values('date').tail(90)
    
    return {
        "dates": subset['date'].dt.strftime('%Y-%m-%d').tolist(),
        "prices": subset['price_ngn'].tolist()
    }

@app.post("/predict")
def predict_future_price(data: MarketData):
    """
    Predicts the next day's price based on current market conditions.
    """
    # 1. Validation
    if data.item_id not in model_warehouse:
        raise HTTPException(status_code=404, detail=f"Model not found for '{data.item_id}'. Available: {list(model_warehouse.keys())}")
    
    # 2. Retrieve the Brain
    artifacts = model_warehouse[data.item_id]
    model = artifacts["model"]
    scaler = artifacts["scaler"]
    required_features = artifacts["features"]

    try:
        # 3. Prepare Input Vector (Smart Filling)
        # Create a DataFrame with 0s matching the exact feature shape used during training
        input_vector = pd.DataFrame(0, index=[0], columns=required_features)
        
        # 4. Fill Key Drivers (Log Transformation)
        # We use np.log because the model was trained on Log Returns
        
        # Fuel Lag 1
        if 'fuel_lag_1' in required_features:
            input_vector['fuel_lag_1'] = np.log(data.fuel_price) if data.fuel_price > 0 else 0
            
        # Diesel Lag 1
        if 'diesel_lag_1' in required_features:
            input_vector['diesel_lag_1'] = np.log(data.diesel_price) if data.diesel_price > 0 else 0
            
        # Target Item Lag 1 (Autoregression)
        target_lag = f"{data.item_id}_lag_1"
        if target_lag in required_features:
            input_vector[target_lag] = np.log(data.current_price) if data.current_price > 0 else 0

        # 5. Scale & Predict
        input_scaled = scaler.transform(input_vector)
        pred_log_return = model.predict(input_scaled)[0]
        
        # 6. Convert Log Return back to Naira Price
        # Formula: New_Price = Old_Price * e^(Log_Return)
        predicted_price = data.current_price * np.exp(pred_log_return)

        return {
            "commodity": data.item_id,
            "current_price": data.current_price,
            "predicted_price_next_day": round(predicted_price, 2),
            "predicted_change_pct": round(pred_log_return * 100, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))