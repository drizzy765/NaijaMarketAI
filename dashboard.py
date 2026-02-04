import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set page config
st.set_page_config(page_title="Naija Market Analysis Dashboard", layout="wide")

st.title("🇳🇬 Naija Market Food Price Analysis")
st.markdown("Interactive dashboard to explore food price trends in Nigeria.")

# File loading logic
data_file_path = "final_dataset (2).csv"

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Check if file exists, else ask for upload
if os.path.exists(data_file_path):
    df = load_data(data_file_path)
    st.success(f"Loaded dataset: `{data_file_path}`")
else:
    st.warning(f"Could not find `{data_file_path}` in the current directory.")
    uploaded_file = st.file_uploader("Please upload the dataset CSV", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['date'] = pd.to_datetime(df['date'])
        st.success("File uploaded successfully!")
    else:
        st.stop()

# Sidebar controls
st.sidebar.header("Filter Options")

# Item selection
available_items = df['item_id'].unique()
selected_item = st.sidebar.selectbox("Select Item", available_items)

# Comparison selection
compare_items = st.sidebar.multiselect("Compare with other items", available_items)

# Date Range Filter
min_date = df['date'].min().date()
max_date = df['date'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter data
mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
filtered_df = df.loc[mask]

item_df = filtered_df[filtered_df['item_id'] == selected_item].sort_values('date')

# Comparison Logic
comparison_data = []
if compare_items:
    comparison_data = [item_df]
    for item in compare_items:
         comp_df = filtered_df[filtered_df['item_id'] == item].sort_values('date')
         comparison_data.append(comp_df)
    
    combined_df = pd.concat(comparison_data)
else:
    combined_df = item_df

# Main Content Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Price Trend: {selected_item}")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=combined_df, x='date', y='price_ngn', hue='item_id', ax=ax)
    
    plt.title(f'Price Trend over Time')
    plt.xlabel('Date')
    plt.ylabel('Price (NGN)')
    plt.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig, use_container_width=False)

with col2:
    st.subheader("Statistics")
    if not item_df.empty:
        stats = item_df['price_ngn'].describe()
        st.write(stats)
        
        current_price = item_df.iloc[-1]['price_ngn']
        st.metric("Latest Price", f"₦{current_price:,.2f}")
        
        max_price = item_df['price_ngn'].max()
        min_price = item_df['price_ngn'].min()
        
        st.write(f"**Highest Price:** ₦{max_price:,.2f}")
        st.write(f"**Lowest Price:** ₦{min_price:,.2f}")
    else:
        st.write("No data available for this selection.")

# Data Table
with st.expander("View Raw Data"):
    st.dataframe(combined_df)
