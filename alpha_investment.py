import streamlit as st
import requests
import pandas as pd
import time

# Alpha Vantage API key
API_KEY = "059VKV2VPORKW7KA"

# Alpha Vantage API URLs
BALANCE_SHEET_URL = "https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={}&apikey={}"
INCOME_STATEMENT_URL = "https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={}&apikey={}"

# Load S&P 500 Tickers
sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()

# Function to fetch most recent QUARTERLY financials
def get_financials(ticker):
    try:
        balance_resp = requests.get(BALANCE_SHEET_URL.format(ticker, API_KEY)).json()
        income_resp = requests.get(INCOME_STATEMENT_URL.format(ticker, API_KEY)).json()

        # Extract Latest QUARTERLY Financial Values
        latest_balance = balance_resp.get("quarterlyReports", [{}])[0]
        latest_income = income_resp.get("quarterlyReports", [{}])[0]

        revenue = float(latest_income.get("totalRevenue", 0))
        cogs = float(latest_income.get("costOfRevenue", 0))
        accounts_receivable = float(latest_balance.get("currentNetReceivables", 0))
        inventory = float(latest_balance.get("inventory", 0))
        accounts_payable = float(latest_balance.get("currentAccountsPayable", 0))

        return revenue, cogs, accounts_receivable, inventory, accounts_payable
    except Exception as e:
        return None, None, None, None, None

# Function to calculate DPO, DIO, DSO, CCC
def calculate_metrics(revenue, cogs, accounts_receivable, inventory, accounts_payable):
    days_in_period = 365
    try:
        dpo = (accounts_payable / cogs) * days_in_period if cogs else None
        dio = (inventory / cogs) * days_in_period if cogs else None
        dso = (accounts_receivable / revenue) * days_in_period if revenue else None
        ccc = dio + dso - dpo if None not in [dio, dso, dpo] else None
        return round(dpo, 2), round(dio, 2), round(dso, 2), round(ccc, 2)
    except Exception as e:
        return None, None, None, None

# Streamlit UI
st.set_page_config(page_title="Cash Conversion Cycle (CCC) Dashboard", layout="wide")
st.title("📊 Cash Conversion Cycle (CCC) Analysis for All S&P 500 Companies")

if st.button("Analyze All Companies"):
    results = []

    for ticker in sp500_tickers:
        st.write(f"🔄 Fetching data for {ticker}...")  # Show progress
        
        revenue, cogs, accounts_receivable, inventory, accounts_payable = get_financials(ticker)

        if None in [revenue, cogs, accounts_receivable, inventory, accounts_payable]:
            st.warning(f"⚠️ Missing financial data for {ticker}. Skipping.")
            continue

        dpo, dio, dso, ccc = calculate_metrics(revenue, cogs, accounts_receivable, inventory, accounts_payable)

        if None not in [dpo, dio, dso, ccc]:
            results.append({"Ticker": ticker, "DPO (Days)": dpo, "DIO (Days)": dio, "DSO (Days)": dso, "CCC (Days)": ccc})

        time.sleep(15)  # Alpha Vantage free tier allows 5 API calls per minute

    # Convert to DataFrame and Display in Streamlit
    if results:
        df_results = pd.DataFrame(results)
        st.write("### 📊 Cash Conversion Cycle Metrics for All Companies")
        st.dataframe(df_results)

st.caption("📈 Data sourced from Alpha Vantage API")
