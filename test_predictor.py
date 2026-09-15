import pandas as pd
import numpy as np
from predictor import predict_stock_price
from data import fetch_stock_data
import datetime

def test_predictor_basic():
    print("Testing basic prediction with real data...")
    # Fetch some real data
    df = fetch_stock_data("AAPL", period="1y")
    if df.empty:
        print("Failed to fetch data for AAPL, skipping real data test.")
        return False
    
    forecast = predict_stock_price(df, days=7)
    
    print(f"Forecast shape: {forecast.shape}")
    print(forecast.head())
    
    assert len(forecast) == 7, f"Expected 7 rows, got {len(forecast)}"
    assert 'ds' in forecast.columns, "Missing 'ds' column"
    assert 'yhat' in forecast.columns, "Missing 'yhat' column"
    assert not forecast['yhat'].isnull().any(), "Forecast contains null values"
    
    # Verify future dates
    last_date = df.index[-1].replace(tzinfo=None)
    first_forecast_date = forecast['ds'].iloc[0]
    assert first_forecast_date > last_date, f"Forecast date {first_forecast_date} should be after last data date {last_date}"
    
    print("Basic prediction test passed!")
    return True

def test_predictor_edge_cases():
    print("\nTesting edge cases...")
    
    # Empty DataFrame
    empty_df = pd.DataFrame()
    assert predict_stock_price(empty_df).empty, "Should return empty for empty input"
    
    # Insufficient data
    small_df = pd.DataFrame({'Close': [100, 101]}, index=pd.date_range('2023-01-01', periods=2))
    assert predict_stock_price(small_df).empty, "Should return empty for insufficient data (<10 rows)"
    
    # Invalid columns
    invalid_df = pd.DataFrame({'Open': range(20)}, index=pd.date_range('2023-01-01', periods=20))
    assert predict_stock_price(invalid_df).empty, "Should return empty for missing 'Close' column"
    
    print("Edge cases test passed!")
    return True

if __name__ == "__main__":
    try:
        success_basic = test_predictor_basic()
        success_edge = test_predictor_edge_cases()
        
        if success_basic and success_edge:
            print("\nALL TESTS PASSED!")
        else:
            print("\nSOME TESTS FAILED!")
            exit(1)
    except Exception as e:
        print(f"\nTEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
