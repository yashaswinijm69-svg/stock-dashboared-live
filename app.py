import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from streamlit_autorefresh import st_autorefresh

from db import init_db, add_to_watchlist, remove_from_watchlist, get_watchlist
from data import fetch_stock_data, fetch_ticker_info
from indicators import compute_sma, compute_ema, compute_rsi, compute_macd
from alerts import check_and_send_alerts
from predictor import predict_stock_price

# Set up page configuration
st.set_page_config(
    page_title="Stock Dashboard Live",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run auto-refresh every 60 seconds (60000 milliseconds)
st_autorefresh(interval=60000, key="data_refresh")

# Initialize database tables on startup
init_db()

# Run price alert checks
check_and_send_alerts()

# Custom CSS for modern visual style
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e9ecef;
            text-align: center;
        }
        .stButton>button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# App Title
st.title("📈 Stock Dashboard Live")

# -------------------------------------------------------------
# Sidebar: User inputs and Watchlist
# -------------------------------------------------------------
st.sidebar.header("🔍 Search Stock")

# Callback function to safely update stock symbol from watchlist click
def select_symbol(sym):
    st.session_state["symbol_input"] = sym

# Initialize session state for symbol if not present
if "symbol_input" not in st.session_state:
    st.session_state["symbol_input"] = "AAPL"

# Ticker symbol input using session state key
symbol_input = st.sidebar.text_input(
    "Enter Stock Symbol:", 
    key="symbol_input",
    max_chars=10, 
    help="e.g. AAPL, MSFT, TSLA, GOOG"
).strip().upper()

# Timeframe/Period select
period = st.sidebar.selectbox(
    "Select Timeframe Period:",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=3, # default to 1y
    help="Duration of historical data to fetch"
)

# Indicator settings in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Indicator Settings")
sma_window = st.sidebar.slider("SMA Window:", min_value=5, max_value=200, value=20, step=5)
ema_window = st.sidebar.slider("EMA Window:", min_value=5, max_value=200, value=50, step=5)
show_sma = st.sidebar.checkbox("Show SMA", value=True)
show_ema = st.sidebar.checkbox("Show EMA", value=True)
show_rsi = st.sidebar.checkbox("Show RSI", value=True)
show_macd = st.sidebar.checkbox("Show MACD", value=True)
show_forecast = st.sidebar.checkbox("Show Prophet Forecast", value=False)

# Watchlist management section
st.sidebar.markdown("---")
st.sidebar.subheader("⭐ Watchlist Manager")

# Form to add/update symbol (uses current symbol_input by default)
alert_price_input = st.sidebar.number_input(
    f"Set Alert Price for {symbol_input} (Optional):",
    min_value=0.0,
    value=0.0,
    step=0.01,
    format="%.2f",
    help="Set a target price to track alongside this stock."
)

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("➕ Add/Update"):
        alert_val = alert_price_input if alert_price_input > 0 else None
        if add_to_watchlist(symbol_input, alert_val):
            st.sidebar.success(f"Added {symbol_input} to Watchlist!")
            st.rerun()
        else:
            st.sidebar.error("Failed to add.")

with col2:
    if st.button("🗑️ Remove"):
        if remove_from_watchlist(symbol_input):
            st.sidebar.info(f"Removed {symbol_input}.")
            st.rerun()
        else:
            st.sidebar.warning(f"Not in Watchlist.")

# Render Watchlist entries
st.sidebar.markdown("### My Watchlist")
watchlist = get_watchlist()
if watchlist:
    for sym, alert in watchlist:
        cols = st.sidebar.columns([3, 2, 1])
        with cols[0]:
            # Clicking the symbol name updates the search field via session state
            st.button(f"📊 {sym}", key=f"wl_btn_{sym}", on_click=select_symbol, args=(sym,))
        with cols[1]:
            if alert:
                st.write(f"${alert:.2f}")
            else:
                st.write("-")
        with cols[2]:
            # Delete button for each item
            if st.button("❌", key=f"wl_del_{sym}"):
                remove_from_watchlist(sym)
                st.rerun()
else:
    st.sidebar.caption("Watchlist is empty.")

# -------------------------------------------------------------
# Main Application Content
# -------------------------------------------------------------
if symbol_input:
    with st.spinner(f"Fetching data for {symbol_input}..."):
        # Fetch data and info
        df = fetch_stock_data(symbol_input, period=period)
        info = fetch_ticker_info(symbol_input)
        
    if not df.empty:
        # Retrieve symbol's alert info from watchlist if set
        symbol_watchlist_item = next((item for item in watchlist if item[0] == symbol_input), None)
        alert_price = symbol_watchlist_item[1] if symbol_watchlist_item else None
        
        # Display Stock Header Details
        company_name = info.get("longName", symbol_input) if info else symbol_input
        sector = info.get("sector", "N/A") if info else "N/A"
        industry = info.get("industry", "N/A") if info else "N/A"
        currency = info.get("currency", "USD") if info else "USD"
        
        st.subheader(f"{company_name} ({symbol_input})")
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if info:
            st.caption(f"Sector: **{sector}** | Industry: **{industry}** | Currency: **{currency}** | 🔄 Last updated: **{now_str}**")
        else:
            st.caption(f"🔄 Last updated: **{now_str}**")
        
        # Calculate technical indicators
        df["SMA"] = compute_sma(df["Close"], window=sma_window)
        df["EMA"] = compute_ema(df["Close"], window=ema_window)
        df["RSI"] = compute_rsi(df["Close"])
        macd_line, macd_signal, macd_diff = compute_macd(df["Close"])
        df["MACD"] = macd_line
        df["MACD_Signal"] = macd_signal
        df["MACD_Diff"] = macd_diff
        
        # Get latest market stats
        latest_row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else latest_row
        
        current_price = latest_row["Close"]
        price_change = current_price - prev_row["Close"]
        price_change_pct = (price_change / prev_row["Close"]) * 100 if prev_row["Close"] else 0.0
        
        # Key metrics row
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Current Price", f"${current_price:.2f}", f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
        m2.metric("High", f"${latest_row['High']:.2f}")
        m3.metric("Low", f"${latest_row['Low']:.2f}")
        m4.metric("Volume", f"{int(latest_row['Volume']):,}")
        
        if alert_price:
            difference = current_price - alert_price
            diff_pct = (difference / alert_price) * 100
            m5.metric("Target Alert Price", f"${alert_price:.2f}", f"{difference:+.2f} ({diff_pct:+.2f}%)")
            
            # Show visual notification banner based on alert trigger
            if current_price >= alert_price:
                st.success(f"🔔 **Alert Triggered!** Current Price (${current_price:.2f}) is **above or equal to** your target alert price of ${alert_price:.2f}.")
            else:
                st.warning(f"⚠️ **Alert Pending:** Current Price (${current_price:.2f}) is **below** your target alert price of ${alert_price:.2f}.")
        else:
            m5.metric("Target Alert Price", "None Set")

        # Create interactive multi-indicator chart using Plotly
        st.markdown("### 📊 Interactive Analysis Chart")
        
        # Setup subplot layout (Row 1: Price + Moving Averages, Row 2: RSI, Row 3: MACD)
        fig = make_subplots(
            rows=3, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.05, 
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=("Price & Overlays", "Relative Strength Index (RSI)", "MACD (Moving Average Convergence Divergence)")
        )
        
        # Plot 1: Price and SMA/EMA Overlays
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="OHLC",
                showlegend=True
            ),
            row=1, col=1
        )
        
        if show_sma:
            fig.add_trace(
                go.Scatter(x=df.index, y=df["SMA"], name=f"SMA ({sma_window})", line=dict(color="#FF9F1C", width=1.5)),
                row=1, col=1
            )
        
        if show_ema:
            fig.add_trace(
                go.Scatter(x=df.index, y=df["EMA"], name=f"EMA ({ema_window})", line=dict(color="#2EC4B6", width=1.5)),
                row=1, col=1
            )
        
        # Add alert price line if defined
        if alert_price:
            fig.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=[alert_price] * len(df), 
                    name="Alert Price", 
                    line=dict(color="#E71D36", dash="dash", width=1.5)
                ),
                row=1, col=1
            )
            
        # Plot 2: RSI Chart
        if show_rsi:
            fig.add_trace(
                go.Scatter(x=df.index, y=df["RSI"], name="RSI (14)", line=dict(color="#9B5DE5", width=1.5)),
                row=2, col=1
            )
            
            # Add RSI oversold/overbought guidelines
            fig.add_trace(
                go.Scatter(
                    x=[df.index[0], df.index[-1]], y=[70, 70], 
                    mode="lines", name="Overbought (70)", 
                    line=dict(color="#E71D36", dash="dot", width=1),
                    showlegend=False
                ),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=[df.index[0], df.index[-1]], y=[30, 30], 
                    mode="lines", name="Oversold (30)", 
                    line=dict(color="#2EC4B6", dash="dot", width=1),
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # Plot 3: MACD Chart
        if show_macd:
            fig.add_trace(
                go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="#011627", width=1.5)),
                row=3, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df["MACD_Signal"], name="Signal", line=dict(color="#E71D36", width=1.2)),
                row=3, col=1
            )
            
            # MACD Histogram colors (green for positive, red for negative)
            hist_colors = ["#2EC4B6" if val >= 0 else "#E71D36" for val in df["MACD_Diff"]]
            fig.add_trace(
                go.Bar(x=df.index, y=df["MACD_Diff"], name="Histogram", marker_color=hist_colors, showlegend=True),
                row=3, col=1
            )
        
        # Update styling layout
        fig.update_layout(
            height=800,
            xaxis_rangeslider_visible=True, # Enable bottom range slider for zoom/pan
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        # Plot Prophet Forecast if enabled
        if show_forecast:
            with st.spinner("Generating 7-day forecast..."):
                forecast_df = predict_stock_price(df, days=7)
                if not forecast_df.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=forecast_df["ds"],
                            y=forecast_df["yhat"],
                            name="Prophet forecast — experimental, not financial advice.",
                            line=dict(color="#E71D36", dash="dash", width=2)
                        ),
                        row=1, col=1
                    )
                else:
                    st.warning("⚠️ Could not generate Prophet forecast. Ensure you have enough historical data.")

        # Render the Plotly charts in Streamlit
        st.plotly_chart(fig, use_container_width=True)
        
        # Interactive expandable Raw Data Explorer
        with st.expander("📁 View Raw Historical Data & Computed Indicators"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            
        # Optional: Render Company Profile Description if available
        if info and "longBusinessSummary" in info:
            with st.expander("🏢 Company Profile & Description"):
                st.write(info["longBusinessSummary"])
                
    else:
        st.error(f"❌ Could not retrieve stock data for ticker '{symbol_input}'. Please verify the symbol is correct and try again.")
else:
    st.info("💡 Please enter a stock symbol in the sidebar to get started!")
