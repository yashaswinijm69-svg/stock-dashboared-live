import pandas as pd
from db import init_db, add_to_watchlist, remove_from_watchlist, get_watchlist
from data import fetch_stock_data, fetch_ticker_info
from indicators import compute_sma, compute_ema, compute_rsi, compute_macd

def test_database():
    print("--- Testing SQLite / SQLAlchemy Database ---")
    init_db()
    
    # Ensure a clean slate
    remove_from_watchlist("AAPL")
    remove_from_watchlist("MSFT")
    
    # 1. Test adding to watchlist
    print("Adding AAPL and MSFT to watchlist...")
    assert add_to_watchlist("AAPL", 150.50) is True, "Failed to add AAPL to watchlist"
    assert add_to_watchlist("MSFT", None) is True, "Failed to add MSFT to watchlist"
    
    # 2. Test reading from watchlist
    watchlist = get_watchlist()
    print("Current Watchlist:", watchlist)
    symbols = [item[0] for item in watchlist]
    assert "AAPL" in symbols, "AAPL missing from watchlist"
    assert "MSFT" in symbols, "MSFT missing from watchlist"
    
    # Check alert price for AAPL
    aapl_alert = next(item[1] for item in watchlist if item[0] == "AAPL")
    assert aapl_alert == 150.50, f"Expected alert price 150.50, got {aapl_alert}"
    
    # 3. Test removing from watchlist
    print("Removing AAPL from watchlist...")
    assert remove_from_watchlist("AAPL") is True, "Failed to remove AAPL"
    
    watchlist_after = get_watchlist()
    symbols_after = [item[0] for item in watchlist_after]
    assert "AAPL" not in symbols_after, "AAPL should have been removed"
    assert "MSFT" in symbols_after, "MSFT should still be present"
    
    # Clean up MSFT
    remove_from_watchlist("MSFT")
    print("✅ Database operations verified successfully!")

def test_data_and_indicators():
    print("\n--- Testing yfinance and Technical Indicators ---")
    symbol = "MSFT"
    
    # 1. Fetch stock data
    print(f"Fetching 3 months of historical data for {symbol}...")
    df = fetch_stock_data(symbol, period="3mo")
    assert not df.empty, f"Failed to fetch stock data for {symbol}"
    assert "Close" in df.columns, f"Close price missing from DataFrame"
    print(f"Retrieved {len(df)} rows of stock data.")
    
    # 2. Compute Indicators
    print("Calculating Technical Indicators...")
    
    # Simple Moving Average (SMA)
    sma = compute_sma(df["Close"], window=10)
    assert len(sma) == len(df), "SMA series length mismatch"
    # SMA has NaNs for the first (window-1) periods
    non_nan_sma = sma.dropna()
    assert len(non_nan_sma) > 0, "SMA calculation returned all NaNs"
    print(f"Calculated SMA successfully.")
    
    # Exponential Moving Average (EMA)
    ema = compute_ema(df["Close"], window=10)
    assert len(ema) == len(df), "EMA series length mismatch"
    non_nan_ema = ema.dropna()
    assert len(non_nan_ema) > 0, "EMA calculation returned all NaNs"
    print(f"Calculated EMA successfully.")
    
    # Relative Strength Index (RSI)
    rsi = compute_rsi(df["Close"], window=14)
    assert len(rsi) == len(df), "RSI series length mismatch"
    print(f"Calculated RSI successfully.")
    
    # MACD
    macd, signal, diff = compute_macd(df["Close"], window_fast=12, window_slow=26, window_sign=9)
    assert len(macd) == len(df), "MACD line length mismatch"
    assert len(signal) == len(df), "MACD signal line length mismatch"
    assert len(diff) == len(df), "MACD histogram length mismatch"
    print(f"Calculated MACD indicators successfully.")
    
    # 3. Ticker Info Fetching
    print(f"Fetching company info for {symbol}...")
    info = fetch_ticker_info(symbol)
    assert info is not None, f"Failed to fetch info for {symbol}"
    assert "longName" in info or "symbol" in info, "Ticker info returned invalid data"
    print(f"Company: {info.get('longName', symbol)}")
    
    print("✅ yfinance fetching and 'ta' calculations verified successfully!")

if __name__ == "__main__":
    try:
        test_database()
        test_data_and_indicators()
        print("\n🎉 All module verifications passed successfully!")
    except AssertionError as e:
        print(f"\n❌ Assertion Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
