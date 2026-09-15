import pandas as pd
from prophet import Prophet
import logging

# Suppress Prophet and cmdstanpy logs to keep the output clean
logging.getLogger('prophet').setLevel(logging.ERROR)
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

# More aggressive suppression for cmdstanpy if needed
for logger_name in ["cmdstanpy", "prophet"]:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.ERROR)
    logger.propagate = False

def predict_stock_price(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    """
    Predicts future stock prices using the Facebook Prophet model.
    
    Args:
        df (pd.DataFrame): The historical OHLCV data with a DatetimeIndex and 'Close' column.
        days (int): Number of days to forecast into the future.
        
    Returns:
        pd.DataFrame: A DataFrame with 'ds' (date) and 'yhat' (predicted value) columns.
                     Returns an empty DataFrame if input is invalid or insufficient.
    """
    if df is None or df.empty or 'Close' not in df.columns or len(df) < 10:
        # Prophet generally needs more than just a few data points to produce a sensible forecast.
        # Requiring at least 10 points as a reasonable threshold.
        return pd.DataFrame()

    try:
        # Prepare data for Prophet
        # Prophet expects 'ds' (datestamp) and 'y' (target)
        prophet_df = df.copy()
        
        # Ensure the index is a DatetimeIndex
        if not isinstance(prophet_df.index, pd.DatetimeIndex):
            try:
                prophet_df.index = pd.to_datetime(prophet_df.index)
            except Exception:
                return pd.DataFrame()
        
        # Reset index to get dates as a column
        prophet_df = prophet_df.reset_index()
        
        # Identify the date column (it might be named 'Date' or 'Datetime')
        date_col = None
        for col in ['Date', 'Datetime', 'index']:
            if col in prophet_df.columns:
                date_col = col
                break
        
        if not date_col:
            # Fallback: find any datetime64 column
            for col in prophet_df.columns:
                if pd.api.types.is_datetime64_any_dtype(prophet_df[col]):
                    date_col = col
                    break
        
        if not date_col:
            return pd.DataFrame()

        # Final preparation: select ds and y
        prophet_df = prophet_df[[date_col, 'Close']].rename(columns={date_col: 'ds', 'Close': 'y'})
        
        # Ensure 'ds' is timezone-naive (Prophet requirement)
        if prophet_df['ds'].dt.tz is not None:
            prophet_df['ds'] = prophet_df['ds'].dt.tz_localize(None)

        # Initialize and fit the model
        # daily_seasonality=True is useful for some stock data, though yfinance daily data is usually 1 point per day.
        model = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True)
        model.fit(prophet_df)

        # Create future dataframe
        # include_history=False would be ideal, but make_future_dataframe includes history by default
        future = model.make_future_dataframe(periods=days)
        
        # Forecast
        forecast = model.predict(future)

        # Extract only the future dates (the last 'days' rows)
        prediction = forecast[['ds', 'yhat']].tail(days)
        
        return prediction

    except Exception as e:
        print(f"Error in prediction: {e}")
        return pd.DataFrame()
