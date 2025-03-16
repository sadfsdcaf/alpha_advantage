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

# Function to fetch financial data
def get_financials(ticker):
    try:
        balance_resp = requests.get(BALANCE_SHEET_URL.format(ticker, API_KEY)).json()
        income_resp = requests.get(INCOME_STATEMENT_URL.format(ticker, API_KEY)).json()

        latest_balance = balance_resp.get("annualReports", [{}])[0]
        latest_income = income_resp.get("annualReports", [{}])[0]

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
st.title("📊 Cash Conversion Cycle (CCC) Analysis")

# Select company
ticker = st.selectbox("Select a Stock Ticker", sp500_tickers)

if st.button("Analyze"):
    revenue, cogs, accounts_receivable, inventory, accounts_payable = get_financials(ticker)

    if None in [revenue, cogs, accounts_receivable, inventory, accounts_payable]:
        st.error("⚠️ Unable to retrieve all necessary financial data. Try another ticker.")
    else:
        dpo, dio, dso, ccc = calculate_metrics(revenue, cogs, accounts_receivable, inventory, accounts_payable)

        if None in [dpo, dio, dso, ccc]:
            st.error("⚠️ Error calculating metrics. Some financial data might be missing.")
        else:
            st.success(f"📌 Financial metrics for {ticker}:")
            
            # Show calculations
            st.markdown(f"""
            - 📌 **Days Payable Outstanding (DPO)**: {dpo:.2f} days  
              **Formula**: `(Accounts Payable / COGS) * 365`  
              **Calculation**: ({accounts_payable:,.2f} / {cogs:,.2f}) * 365  
            
            - 📌 **Days Inventory Outstanding (DIO)**: {dio:.2f} days  
              **Formula**: `(Inventory / COGS) * 365`  
              **Calculation**: ({inventory:,.2f} / {cogs:,.2f}) * 365  

            - 📌 **Days Sales Outstanding (DSO)**: {dso:.2f} days  
              **Formula**: `(Accounts Receivable / Revenue) * 365`  
              **Calculation**: ({accounts_receivable:,.2f} / {revenue:,.2f}) * 365  

            - 📌 **Cash Conversion Cycle (CCC)**: {ccc:.2f} days  
              **Formula**: `DIO + DSO - DPO`  
              **Calculation**: {dio:.2f} + {dso:.2f} - {dpo:.2f}  
            """)

            # Data visualization
            data = pd.DataFrame({"Metric": ["DPO", "DIO", "DSO", "CCC"], "Value": [dpo, dio, dso, ccc]})
            st.bar_chart(data.set_index("Metric"))
          
st.caption("📈 Data sourced from Alpha Vantage API")
