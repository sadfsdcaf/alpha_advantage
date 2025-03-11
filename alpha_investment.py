import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

API_KEY = '059VKV2VPORKW7KA'

def fetch_stock_data(symbol, function='TIME_SERIES_DAILY'):
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&outputsize=full&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'Time Series (Daily)' in data:
        df = pd.DataFrame(data['Time Series (Daily)']).T
        df = df.rename(columns=lambda x: x[3:])
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df.sort_index(inplace=True)
        return df
    else:
        st.error("Error fetching data. Please try again later or check your API key.")
        return pd.DataFrame()

# Streamlit App UI
st.title("📈 Investment Dashboard")

symbol = st.sidebar.text_input("Enter stock symbol:", "AAPL")

# Fetching Data
with st.spinner("Fetching data..."):
    df = fetch_stock_data(symbol)

if not df.empty:
    st.subheader(f"Price Data for {symbol.upper()}")
    st.write(df.tail())

    # Interactive Price Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Price"
    ))

    fig.update_layout(
        title=f"{symbol.upper()} Historical Price Data",
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        xaxis_rangeslider_visible=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Moving Averages
    st.subheader("Moving Averages")
    ma_period = st.slider("Select MA period", min_value=5, max_value=200, value=20, step=5)
    df[f"MA_{ma_period}"] = df['close'].rolling(ma_period).mean()

    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(x=df.index, y=df['close'], name="Close Price"))
    fig_ma.add_trace(go.Scatter(x=df.index, y=df[f"MA_{ma_period}"], name=f"{ma_period}-day MA"))

    fig_ma.update_layout(
        title=f"{symbol.upper()} Close Price and Moving Average",
        yaxis_title='Price (USD)',
        xaxis_title='Date'
    )

    st.plotly_chart(fig_ma, use_container_width=True)

else:
    st.warning("No data available. Try another stock symbol.")

