from typing import Tuple
import pandas as pd
from ta.trend import sma_indicator, ema_indicator, MACD
from ta.momentum import rsi

def compute_sma(series: pd.Series, window: int = 20) -> pd.Series:
    """
    Computes Simple Moving Average (SMA) for a given pandas Series and window.
    
    Args:
        series (pd.Series): Series of close prices.
        window (int): The window size for the SMA.
        
    Returns:
        pd.Series: Calculated SMA values.
    """
    try:
        return sma_indicator(close=series, window=window, fillna=False)
    except Exception as e:
        print(f"Error calculating SMA: {e}")
        return pd.Series(index=series.index, dtype='float64')

def compute_ema(series: pd.Series, window: int = 20) -> pd.Series:
    """
    Computes Exponential Moving Average (EMA) for a given pandas Series and window.
    
    Args:
        series (pd.Series): Series of close prices.
        window (int): The window size for the EMA.
        
    Returns:
        pd.Series: Calculated EMA values.
    """
    try:
        return ema_indicator(close=series, window=window, fillna=False)
    except Exception as e:
        print(f"Error calculating EMA: {e}")
        return pd.Series(index=series.index, dtype='float64')

def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Computes Relative Strength Index (RSI) for a given pandas Series and window.
    
    Args:
        series (pd.Series): Series of close prices.
        window (int): The window size for the RSI.
        
    Returns:
        pd.Series: Calculated RSI values.
    """
    try:
        return rsi(close=series, window=window, fillna=False)
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return pd.Series(index=series.index, dtype='float64')

def compute_macd(
    series: pd.Series, 
    window_fast: int = 12, 
    window_slow: int = 26, 
    window_sign: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Computes Moving Average Convergence Divergence (MACD) for a given pandas Series.
    
    Args:
        series (pd.Series): Series of close prices.
        window_fast (int): Fast period EMA window.
        window_slow (int): Slow period EMA window.
        window_sign (int): Signal period EMA window.
        
    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]: (MACD line, MACD signal line, MACD difference/histogram).
    """
    try:
        macd_obj = MACD(
            close=series, 
            window_slow=window_slow, 
            window_fast=window_fast, 
            window_sign=window_sign, 
            fillna=False
        )
        return macd_obj.macd(), macd_obj.macd_signal(), macd_obj.macd_diff()
    except Exception as e:
        print(f"Error calculating MACD: {e}")
        empty_series = pd.Series(index=series.index, dtype='float64')
        return empty_series, empty_series, empty_series
