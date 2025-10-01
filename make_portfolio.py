import pandas as pd
import os
import json
from datetime import datetime
from nsepython import nse_eq

def auto_update_portfolio(json_date: str, csv_date: str) -> None:
    """Updates portfolio CSV for csv_date using Grok JSON response from json_date.
       Uses NSEPython (not yfinance) to fetch OHLCV data.
    
    Args:
        json_date (str): Date for JSON file in YYYY-MM-DD format (e.g., '2025-09-26').
        csv_date (str): Date for output CSV in YYYY-MM-DD format (e.g., '2025-09-29').
    
    Raises:
        ValueError: If date format is invalid.
        FileNotFoundError: If JSON file or output directory is missing.
        json.JSONDecodeError: If JSON parsing fails.
    """
    try:
        json_target = datetime.strptime(json_date, '%Y-%m-%d')
        datetime.strptime(csv_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD (e.g., 2025-09-26).")
    
    # Always store JSON under "Weekends" for now (mirrors your structure)
    sub_dir = "Weekends"
    json_file = os.path.join("Grok Daily Reviews", sub_dir, f"t_{json_target.strftime('%Y-%m-%d')}.json")
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"JSON file not found: {json_file}")
    
    output_dir = "Portfolio Files"
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, f"{csv_date}.csv")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    signal_content = json.loads(json_data['choices'][0]['message']['content'])
    trades = {trade['symbol']: trade for trade in signal_content['trades'] if trade['action'] != 'remove'}
    portfolio = signal_content['portfolio']
    
    data = []
    for holding in portfolio['holdings']:
        symbol = holding.split(':')[0].strip()
        if symbol in trades:
            trade = trades[symbol]
            shares = trade['shares']
            buy_price = round(trade['amount'] / shares, 2) if shares > 0 else 0.0
            
            try:
                # Fetch NSE equity data
                ohlcv = nse_eq(symbol)
                hist_data = ohlcv.get("data", [])
                # Find row matching json_date
                close_price = None
                for row in hist_data:
                    if row.get("CH_TIMESTAMP") == json_target.strftime("%d-%b-%Y"):
                        close_price = float(row.get("CH_CLOSING_PRICE"))
                        break
                
                if close_price:
                    current_price = round(close_price, 2)
                    total_amount = round(current_price * shares, 2)
                    perct_change = round(((current_price - buy_price) / buy_price) * 100, 2) if buy_price > 0 else 0.0
                else:
                    print(f"No NSE data for {symbol} on {json_date}")
                    current_price = buy_price
                    total_amount = round(buy_price * shares, 2)
                    perct_change = 0.0
            
            except Exception as e:
                print(f"Error fetching NSE data for {symbol}: {e}")
                current_price = buy_price
                total_amount = round(buy_price * shares, 2)
                perct_change = 0.0
            
            data.append({
                'Holding Name': symbol,
                'Buying Price': buy_price,
                'Current Price': current_price,
                'Number of Units': shares,
                'Total Amount': total_amount,
                'Perct Change': perct_change
            })
    
    # Add cash holding
    if portfolio['cash'] > 0:
        data.append({
            'Holding Name': 'Cash',
            'Buying Price': 1.00,
            'Current Price': 1.00,
            'Number of Units': portfolio['cash'],
            'Total Amount': portfolio['cash'],
            'Perct Change': 0.00
        })
    
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    print(f"Updated portfolio file: {csv_file}")

if __name__ == "__main__":
    json_date = input("Enter the JSON date (YYYY-MM-DD): ").strip()
    csv_date = input("Enter the CSV output date (YYYY-MM-DD): ").strip()
    try:
        auto_update_portfolio(json_date, csv_date)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
