import smtplib
import streamlit as st
from email.message import EmailMessage
from data import fetch_stock_data
from db import get_watchlist

def check_and_send_alerts():
    """
    Checks if watchlist symbols have triggered alert prices and sends an email.
    Tracks sent alerts in st.session_state to avoid duplicate notifications.
    """
    watchlist = get_watchlist()
    
    # Check if credentials exist in secrets
    try:
        if "gmail_user" not in st.secrets or "gmail_password" not in st.secrets:
            return
    except Exception:
        # StreamlitSecretNotFoundError or any other error accessing secrets
        return
        
    if "alerts_sent" not in st.session_state:
        st.session_state["alerts_sent"] = {}
        
    for sym, alert_price in watchlist:
        if alert_price is None:
            continue
            
        # Get latest price
        df = fetch_stock_data(sym, period="1d", interval="1d")
        if df.empty:
            continue
            
        current_price = df["Close"].iloc[-1]
        
        # Simple condition: trigger if current price is >= alert price
        if current_price >= alert_price:
            # Check if already sent for this price
            if st.session_state["alerts_sent"].get(sym) == alert_price:
                continue
            
            if send_alert_email(sym, alert_price, current_price):
                st.session_state["alerts_sent"][sym] = alert_price

def send_alert_email(symbol: str, alert_price: float, current_price: float) -> bool:
    """
    Sends an email alert using Gmail SMTP.
    Returns True if sent successfully, False otherwise.
    """
    try:
        sender_email = st.secrets["gmail_user"]
        password = st.secrets["gmail_password"]
        
        msg = EmailMessage()
        msg["Subject"] = f"Price Alert: {symbol} triggered!"
        msg["From"] = sender_email
        msg["To"] = sender_email # Send to self for now
        
        content = f"""
        Alert Triggered for {symbol}!
        
        Current Price: ${current_price:.2f}
        Alert Price Threshold: ${alert_price:.2f}
        
        The stock has reached or exceeded your configured alert price.
        """
        msg.set_content(content)
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(msg)
            
        return True
    except Exception as e:
        # Silently fail or log to standard error in real apps, 
        # but avoid exposing in UI as per requirements
        print(f"Error sending email: {e}")
        return False
