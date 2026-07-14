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
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from screener_job import main

EXCEL_PATH = "data/live_data.xlsx"

FO_LIST = ['AARTIIND','ABB','ADANIENT','ADANIPORTS','ABCAPITAL','ABFRL','ALKEM','AMBUJACEM','APOLLOHOSP','ASHOKLEY','ASIANPAINT','ASTRAL','AUBANK','AUROPHARMA','AXISBANK','BAJAJ-AUTO','BAJFINANCE','BAJAJFINSV','BALKRISIND','BANDHANBNK','BANKBARODA','BEL','BHARATFORG','BHEL','BPCL','BHARTIARTL','BIOCON','BSOFT','BOSCHLTD','BRITANNIA','CANBK','CHAMBLFERT','CHOLAFIN','CIPLA','COALINDIA','COFORGE','COLPAL','CONCOR','CROMPTON','CUMMINSIND','DABUR','DALBHARAT','DIVISLAB','DIXON','DLF','DRREDDY','EICHERMOT','EXIDEIND','GAIL','GLENMARK','GODREJCP','GODREJPROP','GRANULES','GRASIM','HAVELLS','HCLTECH','HDFCAMC','HDFCBANK','HDFCLIFE','HEROMOTOCO','HINDALCO','HAL','HINDCOPPER','HINDPETRO','HINDUNILVR','ICICIBANK','ICICIGI','ICICIPRULI','IDFCFIRSTB','IEX','IOC','IRCTC','IGL','INDUSTOWER','INDUSINDBK','NAUKRI','INFY','INDIGO','ITC','JINDALSTEL','JSWSTEEL','JUBLFOOD','KOTAKBANK','LTF','LT','LAURUSLABS','LICHSGFIN','LTIM','LUPIN','MGL','M&MFIN','M&M','MANAPPURAM','MARICO','MARUTI','MFSL','MPHASIS','MCX','MUTHOOTFIN','NATIONALUM','NESTLEIND','NMDC','NTPC','OBEROIRLTY','ONGC','OFSS','PAGEIND','PERSISTENT','PETRONET','PIIND','PIDILITIND','PEL','POLYCAB','PFC','POWERGRID','PNB','RBLBANK','RECLTD','RELIANCE','MOTHERSON','SBICARD','SBILIFE','SHREECEM','SHRIRAMFIN','SIEMENS','SRF','SBIN','SAIL','SUNPHARMA','SYNGENE','TATACHEM','TATACOMM','TCS','TATACONSUM','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','FEDERALBNK','INDHOTEL','TITAN','TORNTPHARM','TRENT','TVSMOTOR','ULTRACEMCO','UNITDSPR','UPL','VEDL','IDEA','VOLTAS','WIPRO','ZYDUSLIFE','360ONE','ADANIENSOL','ADANIGREEN','AMBER','ANGELONE','APLAPOLLO','ATGL','BANKINDIA','BANKNIFTY','BDL','BLUESTARCO','BSE','CAMS','CDSL','CESC','CGPOWER','CYIENT','DELHIVERY','DMART','ETERNAL','FINNIFTY','FORTIS','GMRAIRPORT','HFCL','HINDZINC','HUDCO','IIFL','INDIANB','INOXWIND','IRB','IREDA','IRFC','JIOFIN','JSL','JSWENERGY','KALYANKJIL','KAYNES','KEI','KFINTECH','KPITTECH','LICI','LODHA','MANKIND','MAXHEALTH','MAZDOCK','MIDCPNIFTY','NBCC','NCC','NHPC','NIFTY','NYKAA','OIL','PATANJALI','PAYTM','PGEL','PHOENIXLTD','PNBHOUSING','POLICYBZR','POONAWALLA','PPLPHARMA','PRESTIGE','RVNL','SJVN','SOLARINDS','SONACOMS','SUPREMEIND','TATAELXSI','TATATECH','TIINDIA','TITAGARH','TORNTPOWER','UNIONBANK','UNOMINDA','VBL','YESBANK']

st.set_page_config(page_title="Live Price Action in NSE", layout="wide")

# Auto-refresh the page every 5 minutes to pick up new data
st_autorefresh(interval=5 * 60 * 1000, key="datarefresh")

def load_data():
    if not os.path.exists(EXCEL_PATH):
        return None, None, None, "No data yet"
    df_5m_price = pd.read_excel(EXCEL_PATH, sheet_name="5m_Price")
    df_5m_vol = pd.read_excel(EXCEL_PATH, sheet_name="5m_Vol")
    df_opening = pd.read_excel(EXCEL_PATH, sheet_name="Opening")
    meta = pd.read_excel(EXCEL_PATH, sheet_name="meta")
    last_updated = meta["last_updated_ist"].iloc[0] if not meta.empty else "Unknown"
    return df_5m_price, df_5m_vol, df_opening, last_updated


def apply_fo_filter(df, enabled, name_col='Symbol', sort_col='% Change'):
    """Filter to F&O stocks only (if enabled) and sort by EMA column if present."""
    if df is None or df.empty:
        return df
    if enabled and name_col in df.columns:
        df = df[df[name_col].isin(FO_LIST)]
    if sort_col in df.columns:
        df = df.sort_values(by=sort_col, ascending=False)
    return df


def highlight_close(row):
    if row.get('Momentum') == 'Bullish':
        return ['background-color: #d4edda; color: green;'] * len(row)
    elif row.get('Momentum') == 'Bearish':
        return ['background-color: #f8d7da; color: red;'] * len(row)
    else:
        return [''] * len(row)


# ---------------- Styling ----------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f4f8;
        color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='text-align: center; color:#4B8BBE;'>Live Price Action in NSE - Free NOW</h1>
    <h3 style='text-align: center; color: gray;'>Where the Smart Money of BIG Fund houses going !!</h3>
    """,
    unsafe_allow_html=True,
)

fo_checkbox = st.checkbox("Only F&O Stocks", value=True)

# ---------------- Load, filter & display data ----------------
df_output_5mP, df_output_5mVol, df_output_open, last_updated = load_data()

df_output_5mP = apply_fo_filter(df_output_5mP, fo_checkbox)
df_output_5mVol = apply_fo_filter(df_output_5mVol, fo_checkbox)
df_output_open = apply_fo_filter(df_output_open, fo_checkbox)

st.markdown(
    f"<p style='text-align: center; color: gray;'>Data last updated (IST): {last_updated} - Next refresh in 5mins</p>",
    unsafe_allow_html=True
)

if df_output_5mP is not None and not df_output_5mP.empty:
    st.subheader("Price Momentum in last 5mins")
    st.dataframe(df_output_5mP.style.apply(highlight_close, axis=1))

if df_output_5mVol is not None and not df_output_5mVol.empty:
    st.subheader("Volume Momentum in last 5mins")
    st.dataframe(df_output_5mVol.style.apply(highlight_close, axis=1))

if df_output_open is not None and not df_output_open.empty:
    st.subheader("Pre-Open Momentum")
    st.dataframe(df_output_open.style.apply(highlight_close, axis=1))

st.markdown(
    """
    <h6 style='text-align: center; color: gray;'> "All a person needs to do is observe what the market is telling him & evaluate it"-Jesse Livermore</h6>
    <h3 style='text-align: center; color:#25AD91;'>Developed by Saurabh Sharma</h3>
    <p style='text-align: center;font-size: 16px; '><a href='mailto:srb_sharma@outlook.com' style='text-align: center;'>Contact @ srb_sharma@outlook.com</a></p>
    <p style='text-align: right; font-size: 11px; font-style: italic; color: gray;'>**Only Stocks with Traded value above 10L</p>
    """,
    unsafe_allow_html=True,
)
