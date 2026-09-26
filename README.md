# 📈 Stock Dashboard Live

An interactive stock market analysis dashboard built using **Python, Streamlit, Plotly, Pandas, yFinance, SQLite, and Prophet**.

The application allows users to search for stocks, visualize historical price movements using interactive candlestick charts, apply technical indicators, maintain a persistent watchlist, configure price alerts with email notifications, and generate an experimental 7-day Prophet forecast.

🌐 **Live Application:**  
[Open Stock Dashboard Live](https://stock-dashboared-live-xjuttfmuylzdhyaoiq4rft.streamlit.app/)

---

## 📌 Project Overview

Stock market data contains a large amount of information that can be difficult to analyze using raw tables alone.

This project provides a simple interactive dashboard where users can enter a stock symbol and analyze its historical market data through visualizations and technical indicators.

The dashboard combines:

- Real-time/historical stock data
- Interactive financial charts
- Technical analysis indicators
- SQLite-based watchlist management
- Automated price-alert notifications
- Experimental machine-learning forecasting
- Automatic dashboard refresh
- Cloud deployment

The application is designed as an educational and portfolio project demonstrating how data acquisition, visualization, database management, notifications, machine learning, and cloud deployment can be integrated into one application.

---

# 🎯 Objectives

The main objectives of this project are:

- To build an interactive stock-market dashboard.
- To retrieve stock-market data programmatically.
- To visualize OHLCV data using candlestick charts.
- To provide commonly used technical indicators.
- To allow users to maintain a stock watchlist.
- To provide configurable price alerts.
- To send email notifications when an alert threshold is reached.
- To experiment with short-term forecasting using Prophet.
- To deploy the application as a publicly accessible web application.

---

# ✨ Key Features

## 📊 1. Stock Search

Users can enter a stock ticker symbol such as:

- `AAPL`
- `MSFT`
- `GOOGL`
- `AMZN`

The dashboard retrieves the corresponding market data and displays the stock information.

The dashboard displays:

- Current price
- High price
- Low price
- Trading volume
- Stock sector
- Industry
- Currency
- Last updated timestamp

---

## 🕯️ 2. Interactive Candlestick Chart

The application uses **Plotly** to display an interactive OHLC candlestick chart.

The chart provides:

- Open price
- High price
- Low price
- Close price
- Interactive hover information
- Zoom
- Pan
- Range slider

Users can interact with the chart to examine different portions of the historical price data.

---

## ⏱️ 3. Timeframe Selection

Users can select the required historical timeframe from the dashboard.

This allows users to analyze different periods of stock-price movement without manually downloading data.

---

# 📈 Technical Analysis

The dashboard supports multiple technical indicators.

## Simple Moving Average — SMA

The SMA calculates the average closing price over a selected number of periods.

It can help visualize the general direction of historical price movement.

The SMA window can be adjusted from the dashboard.

---

## Exponential Moving Average — EMA

EMA gives greater importance to more recent prices compared with SMA.

The dashboard allows users to enable or disable the EMA overlay.

The EMA window can also be adjusted.

---

## Relative Strength Index — RSI

RSI is displayed as a separate indicator section below the main price chart.

The dashboard provides a toggle to show or hide the RSI indicator.

---

## Moving Average Convergence Divergence — MACD

MACD is also displayed in a separate section below the price chart.

The dashboard provides a toggle to show or hide MACD.

---

# ⭐ Watchlist Management

The application provides a SQLite-based watchlist.

Users can:

- Add stock symbols to the watchlist.
- Store an alert price for a stock.
- View tracked stocks.
- Load a watchlist stock into the main dashboard.
- Remove stocks from the watchlist.

The watchlist is managed using SQLite through the project's database module.

---

# 🔔 Price Alert System

The dashboard supports configurable stock-price alerts.

Users can specify a target alert price for a watchlist stock.

The application compares the current stock price with the configured threshold.

The dashboard displays the alert status, such as:

- Alert Pending
- Alert Triggered

---

# 📧 Email Notifications

When an alert threshold is reached, the application can send an email notification using **Gmail SMTP**.

The email notification contains information such as:

- Stock symbol
- Current price
- Configured alert threshold
- Alert status

The application uses Gmail SMTP through Python's `smtplib`.

Credentials are not hardcoded into the application.

They are stored using Streamlit Secrets.

---

# 🔐 Security and Secrets

Sensitive email credentials are kept outside the source code.

The application uses Streamlit Secrets with keys matching the application configuration:

```toml
gmail_user = "your_email@gmail.com"
gmail_password = "your_gmail_app_password"
