import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:8000"

def plot_pro_chart(history_dates, history_prices, item_name, predicted_price=None):
    """Creates a Financial-Style interactive chart with history + prediction."""
    fig = go.Figure()
    # 1. Plot History (Blue Area)
    fig.add_trace(go.Scatter(
        x=history_dates, y=history_prices, mode='lines', name='History',
        line=dict(color='#0066CC', width=3), fill='tozeroy',
        fillcolor='rgba(0, 102, 204, 0.1)'
    ))
    # 2. Plot Prediction Connection (Red Dotted)
    if predicted_price and len(history_dates) > 0:
        last_date = pd.to_datetime(history_dates[-1])
        next_date = last_date + timedelta(days=1)
        last_price = history_prices[-1]
        fig.add_trace(go.Scatter(
            x=[last_date, next_date], y=[last_price, predicted_price],
            mode='lines', name='Forecast',
            line=dict(color='#FF3333', width=3, dash='dot')
        ))
        fig.add_trace(go.Scatter(
            x=[next_date], y=[predicted_price], mode='markers+text',
            name='Next Day', marker=dict(color='#FF3333', size=12, symbol='diamond'),
            text=[f"₦{predicted_price:,.0f}"], textposition="top center"
        ))
    # 3. Layout (Range Slider + Zoom)
    fig.update_layout(
        title=f"{item_name.upper()} Price Analysis",
        yaxis_title="Price (₦)", xaxis_title="Date",
        template="plotly_white", hovermode="x unified", height=500,
        legend=dict(orientation="h", y=1.02, x=1),
        xaxis=dict(
            rangeselector=dict(buttons=[
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(step="all", label="ALL")
            ]),
            rangeslider=dict(visible=True), type="date"
        )
    )
    return fig

st.set_page_config(
    page_title="Naija AgroPulse Prediction",
    page_icon="🇳🇬",
    layout="wide"
)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063823.png", width=50) # Placeholder icon
    st.title("Price Predictor")
    st.markdown("---")
    
    # Input Form
    with st.form("prediction_form"):
        item_id = st.selectbox(
            "Select Commodity",
            options=['rice_local', 'beans_oloyin', 'yam_tuber', 'garri_white', 'bread_loaf']
        )
        
        current_price = st.number_input(
            "Current Market Price (₦)", 
            min_value=0.0, 
            value=50000.0, 
            step=100.0,
            help="Enter the latest known price per bag/unit."
        )
        
        fuel_price = st.number_input(
            "Fuel Price (₦/Liter)", 
            min_value=0.0, 
            value=1000.0, 
            step=10.0
        )
        
        diesel_price = st.number_input(
            "Diesel Price (₦/Liter)", 
            min_value=0.0, 
            value=1200.0, 
            step=10.0
        )
        
        submitted = st.form_submit_button("Generate Prediction", type="primary")

# --- MAIN PAGE ---
st.title("🇳🇬 Naija AgroPulse Dashboard")
st.markdown("###  AI-Powered Price Forecasting")

# Check API Health
try:
    health = requests.get(f"{API_BASE_URL}/", timeout=2)
    if health.status_code == 200:
        st.success(f"Backend Connected: {health.json().get('status')}")
    else:
        st.warning("Backend is reachable but returned an error.")
except requests.exceptions.ConnectionError:
    st.error(" Backend is OFFLINE. Please start the FastAPI server.")
    st.stop()

if submitted:
    # 1. CALL PREDICTION API
    payload = {
        "item_id": item_id,
        "current_price": current_price,
        "fuel_price": fuel_price,
        "diesel_price": diesel_price
    }
    
    with st.spinner("Crunching market numbers..."):
        try:
            response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=5)
            response.raise_for_status()
            pred_data = response.json()
            
            # Extract Data
            pred_price = pred_data["predicted_price_next_day"]
            pct_change = pred_data.get("predicted_change_pct", 0.0)
            
            # Display Metric
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Predicted Price (Next Day)", 
                    value=f"₦{pred_price:,.2f}", 
                    delta=f"{pct_change}%",
                    delta_color="inverse" # Green for down (good for consumers), Red for up? Or standard financial (Green up)?
                    # Standard: Green = Up, Red = Down. 
                    # For inflation context: Red = Price Up (Bad), Green = Price Down (Good).
                    # Streamlit 'inverse' does exactly that (Red for positive delta).
                )
            
        except requests.exceptions.HTTPError as e:
            st.error(f"Prediction Error: {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()
            
    # 2. FETCH HISTORY & PLOT CHART
    st.markdown("---")
    st.subheader(f"Price Trend: {item_id.replace('_', ' ').title()}")
    
    with st.spinner("Fetching historical data..."):
        try:
            hist_response = requests.get(f"{API_BASE_URL}/history/{item_id}", timeout=5)
            hist_response.raise_for_status()
            hist_data = hist_response.json()
            
            if "error" in hist_data:
                st.warning(hist_data["error"])
            else:
                dates = hist_data["dates"]
                prices = hist_data["prices"]
                
                # --- PLOTLY CHART ---
                fig = plot_pro_chart(
                    history_dates=dates,
                    history_prices=prices,
                    item_name=item_id,
                    predicted_price=pred_price
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Could not load chart: {e}")

else:
    st.info(" Adjust parameters in the sidebar and click **Generate Prediction** to see results.")
