import pandas as pd
import yfinance as yf
from typing import Optional, Dict, Any

def fetch_stock_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical OHLCV data from yfinance for a given symbol and period.
    
    Args:
        symbol (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').
        period (str): The time period to retrieve (e.g., '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max').
        interval (str): The frequency interval (e.g., '1d', '1wk', '1mo').
        
    Returns:
        pd.DataFrame: A pandas DataFrame containing OHLCV data with a DatetimeIndex.
                     Returns an empty DataFrame on error or if no data is found.
    """
    try:
        trimmed_symbol = symbol.strip().upper()
        if not trimmed_symbol:
            return pd.DataFrame()
        
        ticker = yf.Ticker(trimmed_symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return pd.DataFrame()
            
        # Ensure standard column names (yfinance sometimes uses capitalized, or multi-index in some versions)
        # Flatten columns if MultiIndex is returned (common in some yfinance versions)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_ticker_info(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetches key statistics/info for a given symbol from yfinance.
    Returns None if info cannot be retrieved or ticker is invalid.
    """
    try:
        trimmed_symbol = symbol.strip().upper()
        if not trimmed_symbol:
            return None
            
        ticker = yf.Ticker(trimmed_symbol)
        info = ticker.info
        if not info or "symbol" not in info and "regularMarketPrice" not in info:
            # Let's verify by trying to fetch fast_info or checking if history exists
            # sometimes ticker.info is empty but ticker.fast_info is available.
            return None
        return info
    except Exception as e:
        print(f"Error fetching ticker info for {symbol}: {e}")
        return None
