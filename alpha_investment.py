import requests
import pandas as pd
import time

# Alpha Vantage API key
API_KEY = "059VKV2VPORKW7KA"

# List of tickers (Example: S&P 500 tickers)
sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()

# Alpha Vantage API base URLs
BALANCE_SHEET_URL = "https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={}&apikey={}"
INCOME_STATEMENT_URL = "https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={}&apikey={}"

# Function to fetch financial data
def get_financials(ticker):
    try:
        # Fetch Balance Sheet Data
        balance_resp = requests.get(BALANCE_SHEET_URL.format(ticker, API_KEY)).json()
        income_resp = requests.get(INCOME_STATEMENT_URL.format(ticker, API_KEY)).json()
        
        # Extract financial values (most recent year)
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
    days_in_period = 365  # Assume 1-year period
    
    try:
        dpo = (accounts_payable / cogs) * days_in_period if cogs else None
        dio = (inventory / cogs) * days_in_period if cogs else None
        dso = (accounts_receivable / revenue) * days_in_period if revenue else None
        ccc = dio + dso - dpo if None not in [dio, dso, dpo] else None
        
        return round(dpo, 2), round(dio, 2), round(dso, 2), round(ccc, 2)
    except Exception as e:
        return None, None, None, None

# Initialize DataFrame to store results
df_results = pd.DataFrame(columns=["Ticker", "DPO", "DIO", "DSO", "CCC"])

# Loop through tickers and analyze financials
for ticker in sp500_tickers:
    print(f"Processing {ticker}...")
    
    revenue, cogs, accounts_receivable, inventory, accounts_payable = get_financials(ticker)
    
    if None in [revenue, cogs, accounts_receivable, inventory, accounts_payable]:
        print(f"Skipping {ticker} due to missing data")
        continue
    
    dpo, dio, dso, ccc = calculate_metrics(revenue, cogs, accounts_receivable, inventory, accounts_payable)
    
    if None not in [dpo, dio, dso, ccc]:
        df_results = df_results.append({
            "Ticker": ticker,
            "DPO": dpo,
            "DIO": dio,
            "DSO": dso,
            "CCC": ccc
        }, ignore_index=True)
    
    # Prevent API rate limits (Alpha Vantage allows 5 requests per minute for free)
    time.sleep(15)

# Save results to CSV
df_results.to_csv("DPO_DIO_DSO_CCC_Analysis.csv", index=False)
print("✅ Analysis complete. Results saved to CSV.")
