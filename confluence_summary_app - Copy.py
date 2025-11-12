import streamlit as st
import random
import time
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
markets = ["NAS100", "US30", "SPX500", "GOLD", "BTCUSD", "EURUSD", "GBPUSD"]
selected_market = st.selectbox("Select Market:", markets)

# -----------------------------
# Mock Data Generation Functions
# -----------------------------
def generate_ema_percentage():
    """Returns a random EMA % above/below"""
    return round(random.uniform(0, 100), 1)

def generate_market_bias():
    """Randomly select Bullish/Bearish/Ranging"""
    bias = random.choice(["Bullish", "Bearish", "Ranging"])
    color = {"Bullish": "#ADD8E6", "Bearish": "#C39BD3", "Ranging": "#FFA500"}
    return bias, color[bias]

def generate_trade_suggestion(total_score, market_bias):
    """Generate Trade Bias based on total score and market bias"""
    if total_score > 70 and market_bias == "Bullish":
        return "High-prob Buy"
    elif total_score > 70 and market_bias == "Bearish":
        return "High-prob Sell"
    elif total_score > 40:
        return "Weak Setup"
    else:
        return "Wait"

def get_session():
    """Return current session based on time"""
    hour = time.localtime().tm_hour
    if 0 <= hour < 8:
        return "Asia"
    elif 8 <= hour < 16:
        return "London"
    else:
        return "NY"

# -----------------------------
# Generate Mock Data
# -----------------------------
weekly = generate_ema_percentage()
daily = generate_ema_percentage()
four_h = generate_ema_percentage()
intraday = generate_ema_percentage()  # Combined 2H,1H,30M,15M

market_bias, bias_color = generate_market_bias()
total_score = round((weekly + daily + four_h + intraday)/4,1)
session_context = get_session()
trade_suggestion = generate_trade_suggestion(total_score, market_bias)

# -----------------------------
# Layout Boxes
# -----------------------------
st.markdown("### EMA Bias / Timeframes")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Weekly", value=f"{weekly} %")
with col2:
    st.metric(label="Daily", value=f"{daily} %")
with col3:
    st.metric(label="4H", value=f"{four_h} %")
with col4:
    st.metric(label="2H,1H,30M,15M", value=f"{intraday} %")

# -----------------------------
# Dark Background Color for Key Boxes
# -----------------------------
dark_bg = "#1E1E1E"  # Almost black / dark grey

# Market Bias Box
st.markdown("### Market Bias")
st.markdown(
    f"<div style='background-color:{dark_bg};padding:15px;border-radius:5px;text-align:center;font-weight:bold;color:{bias_color};'>{market_bias}</div>",
    unsafe_allow_html=True
)

# Total Overall Score
st.markdown("### Total Overall Score")
st.markdown(
    f"<div style='background-color:{dark_bg};padding:15px;border-radius:5px;text-align:center;font-weight:bold;color:#00FF00;'>{total_score} %</div>",
    unsafe_allow_html=True
)

# Session Context & Trade Bias
col5, col6 = st.columns(2)
with col5:
    st.markdown("### Session Context")
    st.markdown(
        f"<div style='background-color:{dark_bg};padding:15px;border-radius:5px;text-align:center;font-weight:bold;color:white;'>{session_context}</div>",
        unsafe_allow_html=True
    )
with col6:
    st.markdown("### Trade Bias / Suggestion")
    st.markdown(
        f"<div style='background-color:{dark_bg};padding:15px;border-radius:5px;text-align:center;font-weight:bold;color:white;'>{trade_suggestion}</div>",
        unsafe_allow_html=True
    )
