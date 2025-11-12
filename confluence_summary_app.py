import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Confluence Summary", layout="wide")
st.title("Confluence Summary")

# -----------------------------
# Auto-refresh every 1 minute
# -----------------------------
st_autorefresh(interval=60*1000, key="confluence_autorefresh")

# -----------------------------
# Dropdown for market selection
# -----------------------------
markets = {
    "NAS100": "^IXIC",
    "US30": "^DJI",
    "SPX500": "^GSPC",
    "GOLD": "GC=F",
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X"
}
selected_market_name = st.selectbox("Select Market:", list(markets.keys()))
selected_market = markets[selected_market_name]

# -----------------------------
# Fetch Data from Yahoo Finance
# -----------------------------
def get_data(symbol, period="60d", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if df.empty:
            return None
        return df
    except:
        return None

def calculate_ema(df, period=50):
    return df['Close'].ewm(span=period, adjust=False).mean()

def get_pdh_pdl(df):
    """Return previous day high and low as scalars"""
    if df is None or len(df) < 2:
        return None, None
    return float(df['High'].iloc[-2]), float(df['Low'].iloc[-2])

# -----------------------------
# Multi-timeframe EMA % Calculation
# -----------------------------
timeframes = {
    "Weekly": "1wk",
    "Daily": "1d",
    "4H": "4h",
    "2H": "2h",
    "1H": "1h",
    "30M": "30m",
    "15M": "15m"
}

valid_intervals = ["1m","2m","5m","15m","30m","60m","90m","1h","4h","1d","5d","1wk","1mo","3mo"]

emas = {}
for tf_label, tf in timeframes.items():
    if tf not in valid_intervals:
        emas[tf_label] = None
        continue
    df = get_data(selected_market, period="60d", interval=tf)
    if df is not None and not df.empty:
        ema_val = calculate_ema(df, 50).iloc[-1]
        current_price = df['Close'].iloc[-1]
        percent_diff = ((current_price - ema_val) / ema_val) * 100
        emas[tf_label] = round(float(percent_diff), 2)
    else:
        emas[tf_label] = None

# Average intraday EMA for combined box
intraday_percents = [emas[tf] for tf in ["2H","1H","30M","15M"] if emas[tf] is not None]
intraday_avg = round(sum(intraday_percents)/len(intraday_percents), 2) if intraday_percents else None

# -----------------------------
# Determine Market Bias using PDH/PDL
# -----------------------------
daily_df = get_data(selected_market, period="10d", interval="1d")
if daily_df is not None and not daily_df.empty:
    pdh, pdl = get_pdh_pdl(daily_df)
    current_close = float(daily_df['Close'].iloc[-1])
else:
    pdh, pdl, current_close = None, None, None

if pdh is None or pdl is None or current_close is None:
    market_bias = "N/A"
else:
    if current_close > pdh:
        market_bias = "Bullish"
    elif current_close < pdl:
        market_bias = "Bearish"
    else:
        market_bias = "Ranging"

# -----------------------------
# Total Overall Score
# -----------------------------
score_components = [emas["Weekly"], emas["Daily"], emas["4H"], intraday_avg]
score_components = [abs(x) for x in score_components if x is not None]

total_score = round(sum(score_components)/len(score_components), 1) if score_components else None

# -----------------------------
# Trade Suggestion Logic
# -----------------------------
if total_score is None:
    trade_suggestion = "N/A"
else:
    if market_bias == "Bullish" and total_score < 3:
        trade_suggestion = "High-prob Buy"
    elif market_bias == "Bearish" and total_score < 3:
        trade_suggestion = "High-prob Sell"
    elif total_score < 5:
        trade_suggestion = "Weak Setup"
    else:
        trade_suggestion = "Wait"

# -----------------------------
# Session Context
# -----------------------------
hour = datetime.now().hour
if 0 <= hour < 8:
    session_context = "Asia"
elif 8 <= hour < 16:
    session_context = "London"
else:
    session_context = "NY"

# -----------------------------
# Layout Boxes
# -----------------------------
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("### EMA Bias / Timeframes (vs 50 EMA)")
col1, col2, col3, col4 = st.columns(4)
with col1:
    val = emas['Weekly']
    st.metric(label="Weekly", value=f"{val:+}%" if val is not None else "N/A")
with col2:
    val = emas['Daily']
    st.metric(label="Daily", value=f"{val:+}%" if val is not None else "N/A")
with col3:
    val = emas['4H']
    st.metric(label="4H", value=f"{val:+}%" if val is not None else "N/A")
with col4:
    val = intraday_avg
    st.metric(label="2H,1H,30M,15M", value=f"{val:+}%" if val is not None else "N/A")

# Market Bias Box
st.markdown("### Market Bias")
st.markdown(
    f"<div style='background-color:#1a1a1a;padding:15px;border-radius:5px;text-align:center;font-weight:bold;color:#FFFFFF;'>{market_bias}</div>",
    unsafe_allow_html=True
)

# Total Overall Score
st.markdown("### Total Overall Score")
st.markdown(
    f"<div style='background-color:#1a1a1a;padding:15px;border-radius:5px;text-align:center;font-weight:bold;color:#00FF00;'>{total_score if total_score is not None else 'N/A'} %</div>",
    unsafe_allow_html=True
)

# Session Context & Trade Bias
col5, col6 = st.columns(2)
with col5:
    st.markdown("### Session Context")
    st.markdown(
        f"<div style='background-color:#1a1a1a;padding:15px;border-radius:5px;text-align:center;font-weight:bold;color:#FFFFFF;'>{session_context}</div>",
        unsafe_allow_html=True
    )
with col6:
    st.markdown("### Trade Bias / Suggestion")
    st.markdown(
        f"<div style='background-color:#1a1a1a;padding:15px;border-radius:5px;text-align:center;font-weight:bold;color:#FFFFFF;'>{trade_suggestion}</div>",
        unsafe_allow_html=True
    )
