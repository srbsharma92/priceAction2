#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit UI — reads pre-computed data from data/live_data.xlsx.
The Excel file is generated separately by screener_job.py, run on a
schedule via GitHub Actions. This app never calls the scraper itself.
"""
import os
import streamlit as st
import pandas as pd
from datetime import datetime, time as dtime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from screener_job import main

EXCEL_PATH = "data/live_data.xlsx"
IST = pytz.timezone("Asia/Kolkata")

FO_LIST = ['AARTIIND','ABB','ADANIENT','ADANIPORTS','ABCAPITAL','ABFRL','ALKEM','AMBUJACEM','APOLLOHOSP','ASHOKLEY','ASIANPAINT','ASTRAL','AUBANK','AUROPHARMA','AXISBANK','BAJAJ-AUTO','BAJFINANCE','BAJAJFINSV','BALKRISIND','BANDHANBNK','BANKBARODA','BEL','BHARATFORG','BHEL','BPCL','BHARTIARTL','BIOCON','BSOFT','BOSCHLTD','BRITANNIA','CANBK','CHAMBLFERT','CHOLAFIN','CIPLA','COALINDIA','COFORGE','COLPAL','CONCOR','CROMPTON','CUMMINSIND','DABUR','DALBHARAT','DIVISLAB','DIXON','DLF','DRREDDY','EICHERMOT','EXIDEIND','GAIL','GLENMARK','GODREJCP','GODREJPROP','GRANULES','GRASIM','HAVELLS','HCLTECH','HDFCAMC','HDFCBANK','HDFCLIFE','HEROMOTOCO','HINDALCO','HAL','HINDCOPPER','HINDPETRO','HINDUNILVR','ICICIBANK','ICICIGI','ICICIPRULI','IDFCFIRSTB','IEX','IOC','IRCTC','IGL','INDUSTOWER','INDUSINDBK','NAUKRI','INFY','INDIGO','ITC','JINDALSTEL','JSWSTEEL','JUBLFOOD','KOTAKBANK','LTF','LT','LAURUSLABS','LICHSGFIN','LTIM','LUPIN','MGL','M&MFIN','M&M','MANAPPURAM','MARICO','MARUTI','MFSL','MPHASIS','MCX','MUTHOOTFIN','NATIONALUM','NESTLEIND','NMDC','NTPC','OBEROIRLTY','ONGC','OFSS','PAGEIND','PERSISTENT','PETRONET','PIIND','PIDILITIND','PEL','POLYCAB','PFC','POWERGRID','PNB','RBLBANK','RECLTD','RELIANCE','MOTHERSON','SBICARD','SBILIFE','SHREECEM','SHRIRAMFIN','SIEMENS','SRF','SBIN','SAIL','SUNPHARMA','SYNGENE','TATACHEM','TATACOMM','TCS','TATACONSUM','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','FEDERALBNK','INDHOTEL','TITAN','TORNTPHARM','TRENT','TVSMOTOR','ULTRACEMCO','UNITDSPR','UPL','VEDL','IDEA','VOLTAS','WIPRO','ZYDUSLIFE','360ONE','ADANIENSOL','ADANIGREEN','AMBER','ANGELONE','APLAPOLLO','ATGL','BANKINDIA','BANKNIFTY','BDL','BLUESTARCO','BSE','CAMS','CDSL','CESC','CGPOWER','CYIENT','DELHIVERY','DMART','ETERNAL','FINNIFTY','FORTIS','GMRAIRPORT','HFCL','HINDZINC','HUDCO','IIFL','INDIANB','INOXWIND','IRB','IREDA','IRFC','JIOFIN','JSL','JSWENERGY','KALYANKJIL','KAYNES','KEI','KFINTECH','KPITTECH','LICI','LODHA','MANKIND','MAXHEALTH','MAZDOCK','MIDCPNIFTY','NBCC','NCC','NHPC','NIFTY','NYKAA','OIL','PATANJALI','PAYTM','PGEL','PHOENIXLTD','PNBHOUSING','POLICYBZR','POONAWALLA','PPLPHARMA','PRESTIGE','RVNL','SJVN','SOLARINDS','SONACOMS','SUPREMEIND','TATAELXSI','TATATECH','TIINDIA','TITAGARH','TORNTPOWER','UNIONBANK','UNOMINDA','VBL','YESBANK']

st.set_page_config(
    page_title="NSE Live Price Action | Smart Money Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Auto-refresh the page every 5 minutes to pick up new data
st_autorefresh(interval=5 * 60 * 1000, key="datarefresh")

def is_nse_market_open():
    """True during actual NSE cash market hours: Mon-Fri, 09:15-15:30 IST."""
    now_ist = datetime.now(pytz.utc).astimezone(IST)
    if now_ist.weekday() > 4:  # Sat=5, Sun=6
        return False
    return dtime(9, 3) <= now_ist.time() <= dtime(15, 30)


def load_data():
    
    if not os.path.exists(EXCEL_PATH):
        return None, None, None, None, None, "No data yet"
    df_5m_price = pd.read_excel(EXCEL_PATH, sheet_name="5m_Price")
    df_5m_vol = pd.read_excel(EXCEL_PATH, sheet_name="5m_Vol")
    df_15m_price = pd.read_excel(EXCEL_PATH, sheet_name="15m_Price")
    df_15m_vol = pd.read_excel(EXCEL_PATH, sheet_name="15m_Vol")
    df_opening = pd.read_excel(EXCEL_PATH, sheet_name="Opening")
    meta = pd.read_excel(EXCEL_PATH, sheet_name="meta")
    last_updated = meta["last_updated_ist"].iloc[0] if not meta.empty else "Unknown"
    return df_5m_price, df_5m_vol, df_15m_price, df_15m_vol, df_opening, last_updated


def apply_fo_filter(df, enabled, name_col='Stock Name', sort_col=None):
    """Filter to F&O stocks only (if enabled) and sort by the given column if present."""
    if df is None or df.empty:
        return df
    if enabled and name_col in df.columns:
        df = df[df[name_col].isin(FO_LIST)]
    if sort_col is not None and sort_col in df.columns:
        df = df.sort_values(by=sort_col, ascending=False)
    return df


def highlight_close(row):
    if row.get('Momentum') == 'Bullish':
        return ['background-color: #d4edda; color: green;'] * len(row)
    elif row.get('Momentum') == 'Bearish':
        return ['background-color: #f8d7da; color: red;'] * len(row)
    else:
        return [''] * len(row)


# Purely cosmetic Styler wrapper — chained on top of highlight_close, does not
# alter any values, columns, or the Bullish/Bearish logic itself. Only the
# background_color / color / border-color / font-weight / text-align /
# font-style properties are honored by st.dataframe's Styler support; the
# table_styles (header row) additionally apply when rendered via st.table.
def theme_table(styler):
    return (
        styler
        .set_properties(**{
            'border-color': 'rgba(212,175,55,0.18)',
            'font-weight': '500',
            'text-align': 'center',
        })
        .set_table_styles([
            {
                'selector': 'thead th',
                'props': [
                    ('background-color', '#D4AF37'),
                    ('color', '#0b1420'),
                    ('font-weight', '700'),
                    ('text-transform', 'uppercase'),
                    ('letter-spacing', '0.5px'),
                    ('font-size', '12.5px'),
                    ('text-align', 'center'),
                    ('padding', '10px 12px'),
                    ('border-bottom', '2px solid #B8912C'),
                ]
            },
            {
                'selector': 'tbody td',
                'props': [
                    ('padding', '8px 12px'),
                    ('border-bottom', '1px solid rgba(212,175,55,0.12)'),
                ]
            },
            {
                'selector': 'table',
                'props': [
                    ('border-collapse', 'collapse'),
                    ('width', '100%'),
                ]
            },
        ])
    )


# ============================= Streamlit UI part =============================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* App background — deep navy finance terminal */
    .stApp {
        background: radial-gradient(circle at top left, #101b2d 0%, #0b1420 45%, #060a12 100%);
        color: #E7ECF3;
    }

    /* Kill default streamlit padding clutter at top */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1150px;
    }

    /* Hero header card */
    .hero-card {
        background: linear-gradient(135deg, rgba(20,33,54,0.95) 0%, rgba(11,20,32,0.95) 100%);
        border: 1px solid rgba(212,175,55,0.35);
        border-radius: 18px;
        padding: 2rem 2.2rem 1.5rem 2.2rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.45);
        text-align: center;
    }

    .hero-eyebrow {
        letter-spacing: 3px;
        font-size: 12px;
        font-weight: 600;
        color: #D4AF37;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #F4E4A6 0%, #D4AF37 45%, #F4E4A6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        color: #9DAAC0;
        margin-top: 0.5rem;
        font-weight: 500;
        letter-spacing: 0.3px;
    }

    /* Toolbar — single horizontal control bar */
    .controls-card {
        background: linear-gradient(135deg, rgba(20,33,54,0.9) 0%, rgba(13,22,36,0.9) 100%);
        border: 1px solid rgba(212,175,55,0.22);
        border-radius: 14px;
        padding: 0.85rem 1.4rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    /* Vertically align the checkbox with the button in the same row */
    .controls-card [data-testid="stVerticalBlock"] {
        display: flex;
        justify-content: center;
    }
    .controls-card .stCheckbox {
        margin-top: 0.35rem;
    }

    /* Live-status timestamp pill (right-aligned in toolbar) */
    .status-pill-wrap {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        height: 100%;
        margin-top: 0.35rem;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 16px;
        border-radius: 999px;
        background: rgba(212,175,55,0.08);
        border: 1px solid rgba(212,175,55,0.35);
        color: #E7ECF3;
        font-size: 12.5px;
        font-weight: 600;
        letter-spacing: 0.4px;
        white-space: nowrap;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #3ED598;
        box-shadow: 0 0 0 0 rgba(62,213,152,0.6);
        animation: pulse-dot 2s infinite;
        flex-shrink: 0;
    }
    .status-dot.closed {
        background: #E5484D;
        box-shadow: 0 0 0 0 rgba(229,72,77,0.6);
        animation: pulse-dot-closed 2s infinite;
    }
    @keyframes pulse-dot-closed {
        0%   { box-shadow: 0 0 0 0 rgba(229,72,77,0.55); }
        70%  { box-shadow: 0 0 0 7px rgba(229,72,77,0); }
        100% { box-shadow: 0 0 0 0 rgba(229,72,77,0); }
    }
    @keyframes pulse-dot {
        0%   { box-shadow: 0 0 0 0 rgba(62,213,152,0.55); }
        70%  { box-shadow: 0 0 0 7px rgba(62,213,152,0); }
        100% { box-shadow: 0 0 0 0 rgba(62,213,152,0); }
    }
    .status-label {
        color: #D4AF37;
        font-weight: 700;
    }

    /* Tabs — restyled to match the navy/gold terminal theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #101C2E !important;
        border: 1px solid rgba(212,175,55,0.25);
        border-radius: 12px;
        padding: 6px;
        margin-top: 0.4rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 10px 20px;
        border-radius: 8px;
        background-color: rgba(212,175,55,0.22) !important;
        color: #F4E4A6 !important;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.02rem;
        letter-spacing: 0.3px;
        border: 1px solid rgba(212,175,55,0.35);
        transition: all 0.15s ease-in-out;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #F4E4A6 !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(212,175,55,0.34) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4AF37 0%, #B8912C 100%) !important;
        color: #0b1420 !important;
        box-shadow: 0 4px 14px rgba(212,175,55,0.35);
        border: 1px solid rgba(212,175,55,0.6);
    }
    .stTabs [aria-selected="true"] p {
        color: #0b1420 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.4rem;
    }

    /* Section badges above each table */
    .section-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 1.1rem 0 0.6rem 0;
        padding: 10px 16px;
        border-radius: 10px;
        background: linear-gradient(90deg, rgba(212,175,55,0.12) 0%, rgba(212,175,55,0.02) 100%);
        border-left: 3px solid #D4AF37;
    }
    .section-badge .icon {
        font-size: 20px;
    }
    .section-badge .label {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F0E6C8;
        letter-spacing: 0.2px;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #B8912C 100%);
        color: #0b1420;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        letter-spacing: 0.4px;
        box-shadow: 0 4px 14px rgba(212,175,55,0.25);
        transition: all 0.15s ease-in-out;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(212,175,55,0.4);
        color: #0b1420;
    }

    /* Checkbox label styling */
    .stCheckbox label p {
        font-weight: 600 !important;
        color: #E7ECF3 !important;
    }

    /* Table container polish (st.table renders real HTML) */
    [data-testid="stTable"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(212,175,55,0.25);
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    }
    [data-testid="stTable"] table {
        background-color: #0F1A2C;
    }
    [data-testid="stTable"] tbody tr:hover td {
        filter: brightness(1.12);
    }

    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.08);
    }

    /* Footer */
    .footer-quote {
        text-align: center;
        color: #8A96AA;
        font-style: italic;
        font-size: 0.92rem;
        margin-top: 2.4rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(255,255,255,0.08);
    }
    .footer-name {
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.3rem;
        color: #D4AF37;
        margin-top: 0.4rem;
    }
    .footer-contact a {
        color: #9DAAC0 !important;
        text-decoration: none;
        font-weight: 500;
    }
    .footer-contact a:hover {
        color: #D4AF37 !important;
    }
    .footer-note {
        text-align: right;
        font-size: 11px;
        font-style: italic;
        color: #64708A;
        margin-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
     """
     <div class="hero-card">
        <div class="hero-eyebrow">NSE &nbsp;•&nbsp; Institutional Grade Screener</div>
        <div class="hero-title">Live Price Action Terminal</div>
        <div class="hero-subtitle">Track where the Smart Money of Big Fund Houses is moving — in real time</div>
     </div>
     """,
     unsafe_allow_html=True,
)

# ---------------- Load data (unchanged logic) ----------------
df_output_5mP, df_output_5mVol, df_output_15mP, df_output_15mVol, df_output_open, last_updated = load_data()

st.markdown('<div class="controls-card">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.4])  # Checkbox | Live status

with col1:
    fo_checkbox = st.checkbox("Only F&O Stocks", value=True)

with col2:
    market_open = is_nse_market_open()
    dot_class = "status-dot" if market_open else "status-dot closed"
    status_text = "LIVE" if market_open else "CLOSED"
    st.markdown(
        f"<div class='status-pill-wrap'><span class='status-pill'>"
        f"<span class='{dot_class}'></span>"
        f"<span class='status-label'>{status_text}</span> &nbsp;•&nbsp; Updated (IST): {last_updated} &nbsp;•&nbsp; Next refresh in 5mins"
        f"</span></div>",
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Filter data (unchanged logic) ----------------
df_output_5mP = apply_fo_filter(df_output_5mP, fo_checkbox, sort_col='Price Change% in 5mins')
df_output_5mVol = apply_fo_filter(df_output_5mVol, fo_checkbox, sort_col='Volume Change% in 5mins')
df_output_15mP = apply_fo_filter(df_output_15mP, fo_checkbox, sort_col='Price Change% in 15mins')
df_output_15mVol = apply_fo_filter(df_output_15mVol, fo_checkbox, sort_col='Volume Change% in 15mins')
df_output_open = apply_fo_filter(df_output_open, fo_checkbox, sort_col='Opening Gap')

tab_5m, tab_15m, tab_open = st.tabs(["⏱️ 5 Minutes", "⏳ 15 Minutes", "🔔 Pre-Open Market"])

# ===================== SECTION 1: 5 MINUTES =====================
with tab_5m:
    if df_output_5mP is not None and not df_output_5mP.empty:
        st.markdown(
            "<div class='section-badge'><span class='icon'>⚡</span><span class='label'>Price Momentum in Last 5 Mins</span></div>",
            unsafe_allow_html=True
        )
        styled_5mP = df_output_5mP.style.apply(highlight_close, axis=1)
        styled_5mP = theme_table(styled_5mP)
        st.table(styled_5mP)
    if df_output_5mVol is not None and not df_output_5mVol.empty:
        st.markdown(
            "<div class='section-badge'><span class='icon'>📊</span><span class='label'>Volume Momentum in Last 5 Mins</span></div>",
            unsafe_allow_html=True
        )
        styled_5mVol = df_output_5mVol.style.apply(highlight_close, axis=1)
        styled_5mVol = theme_table(styled_5mVol)
        st.table(styled_5mVol)

# ===================== SECTION 2: 15 MINUTES =====================
with tab_15m:
    if df_output_15mP is not None and not df_output_15mP.empty:
        st.markdown(
            "<div class='section-badge'><span class='icon'>⚡</span><span class='label'>Price Momentum in Last 15 Mins</span></div>",
            unsafe_allow_html=True
        )
        styled_15mP = df_output_15mP.style.apply(highlight_close, axis=1)
        styled_15mP = theme_table(styled_15mP)
        st.table(styled_15mP)
    if df_output_15mVol is not None and not df_output_15mVol.empty:
        st.markdown(
            "<div class='section-badge'><span class='icon'>📊</span><span class='label'>Volume Momentum in Last 15 Mins</span></div>",
            unsafe_allow_html=True
        )
        styled_15mVol = df_output_15mVol.style.apply(highlight_close, axis=1)
        styled_15mVol = theme_table(styled_15mVol)
        st.table(styled_15mVol)

# ===================== SECTION 3: PRE-OPEN MARKET =====================
with tab_open:
    if df_output_open is not None and not df_output_open.empty:
        st.markdown(
            "<div class='section-badge'><span class='icon'>🔔</span><span class='label'>Pre-Open Momentum</span></div>",
            unsafe_allow_html=True
        )
        styled_open = df_output_open.style.apply(highlight_close, axis=1)
        styled_open = theme_table(styled_open)
        st.table(styled_open)

st.markdown(
    """
    <div class="footer-quote">"All a person needs to do is observe what the market is telling him &amp; evaluate it" — Jesse Livermore</div>
    <div class="footer-name">Developed by Saurabh Sharma</div>
    <p class="footer-contact" style='text-align: center;font-size: 15px; margin-top:0.3rem;'><a href='mailto:srb_sharma@outlook.com'>✉️ Contact @ srb_sharma@outlook.com</a></p>
    <p class="footer-note">**Only Stocks with Traded value above 10L</p>
    """,
    unsafe_allow_html=True,
)
