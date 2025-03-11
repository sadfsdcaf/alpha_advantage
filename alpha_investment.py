import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

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


def fetch_fundamentals(symbol):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data

# RSI
def fetch_technical_indicator(symbol, indicator="RSI", interval="daily", time_period=14):
    url = (f'https://www.alphavantage.co/query?function={indicator}&symbol={symbol}&interval={interval}&'
           f'time_period={time_period}&series_type=close&apikey={API_KEY}')
    response = requests.get(url)
    data = response.json()

    indicator_key = f'Technical Analysis: {indicator}'
    if indicator_key in data:
        df = pd.DataFrame(data[indicator_key]).T
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df.sort_index(inplace=True)
        return df
    else:
        st.error(f"Could not fetch {indicator}")
        return pd.DataFrame()

# Streamlit UI
st.title("📊 Enhanced Investment Dashboard")

symbol = st.sidebar.text_input("Stock symbol:", "AAPL")

with st.spinner("Fetching data..."):
    price_df = fetch_stock_data(symbol)
    fundamentals = fetch_fundamentals(symbol)
    rsi_df = fetch_technical_indicator(symbol, "RSI")

if not price_df.empty:
    st.header(f"{symbol.upper()} - Fundamentals")

    col1, col2, col3 = st.columns(3)
    col1.metric("Market Cap", f"{fundamentals.get('MarketCapitalization', 'N/A')}")
    col2.metric("EPS", f"{fundamentals.get('EPS', 'N/A')}")
    col3.metric("P/E Ratio", f"{fundamentals.get('PERatio', 'N/A')}")

    st.header("Price History")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=price_df.index,
        open=price_df['open'],
        high=price_df['high'],
        low=price_df['low'],
        close=price_df['close'],
        name="Price"
    ))
    fig.update_layout(yaxis_title='Price (USD)', xaxis_title='Date', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    if not rsi_df.empty:
        st.header("RSI (Relative Strength Index)")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=rsi_df.index, y=rsi_df['RSI'], name="RSI"))
        fig_rsi.update_layout(yaxis_title='RSI', xaxis_title='Date')
        st.plotly_chart(fig_rsi, use_container_width=True)

else:
    st.warning("No data available. Please check the stock symbol.")
