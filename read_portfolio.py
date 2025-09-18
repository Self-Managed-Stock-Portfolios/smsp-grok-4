import pandas as pd
import os
from datetime import datetime

def get_portfolio_string(date_input: str) -> str:
    """
    Reads the portfolio CSV for the given date and returns a formatted portfolio string.
    
    Args:
        date_input (str): Date in YYYY-MM-DD format.
    
    Returns:
        str: Formatted portfolio string.
    
    Raises:
        ValueError: If date format is invalid.
        FileNotFoundError: If CSV file does not exist.
        ValueError: If CSV is missing required columns.
    """
    output_dir = "Portfolio Files"
    
    try:
        target_date = datetime.strptime(date_input, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD (e.g., 2025-09-17).")
    
    csv_file = os.path.join(output_dir, f"{target_date.strftime('%Y-%m-%d')}.csv")
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"No portfolio file found for {target_date.strftime('%Y-%m-%d')}. Please create it first.")
    
    df = pd.read_csv(csv_file)
    required_cols = ['Holding Name', 'Buying Price', 'Current Price', 'Number of Units', 'Total Amount', 'Perct Change']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("CSV missing required columns. Expected: Holding Name, Buying Price, Current Price, Number of Units, Total Amount, Perct Change")
    
    total_invested = (df['Buying Price'] * df['Number of Units']).sum()
    total_portfolio_value = df['Total Amount'].sum()
    total_pct_change = ((total_portfolio_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
    
    portfolio_str = f"Total Portfolio Value: ₹{total_portfolio_value:.2f} (Invested: ₹{total_invested:.2f}, Change: {total_pct_change:+.2f}%)\n\n"
    portfolio_str += "Holdings:\n"
    for _, row in df.iterrows():
        pct_change = row['Perct Change']
        portfolio_str += f"- {row['Holding Name']}: {int(row['Number of Units'])} units @ Buy ₹{row['Buying Price']:.2f}, Current ₹{row['Current Price']:.2f}, Value ₹{row['Total Amount']:.2f}, Change {pct_change:+.2f}%\n"
    
    return portfolio_str