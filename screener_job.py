#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runs the screener logic and writes results to data/live_data.xlsx.
This script is executed on a schedule by GitHub Actions
(.github/workflows/update_data.yml), NOT by the Streamlit app.
"""
import sys
import pandas as pd
from datetime import datetime, time as dtime
import pytz

IST = pytz.timezone('Asia/Kolkata')


def is_market_open(now_ist: datetime) -> bool:
    """NSE cash market: Mon-Fri, 09:00-15:30 IST (widened for pre-open data)."""
    if now_ist.weekday() >= 5:  # Sat=5, Sun=6
        return False
    start = dtime(9, 0)
    end = dtime(15, 30)
    return start <= now_ist.time() <= end


def screener():
    """
    >>> PASTE YOUR ACTUAL SCREENER LOGIC HERE <

    This must return four DataFrames in this order:
        df            - (kept for compatibility, not written to Excel unless you want it)
        df_5m_Price   - Price momentum table, must include a 'Momentum' column
                         with values 'Bullish' / 'Bearish' / other
        df_5m_Vol     - Volume momentum table, same 'Momentum' column convention
        df_opening    - Pre-open momentum table, same 'Momentum' column convention

    Replace the placeholder code below with your real requests/API calls
    and calculations.
    """
    # --- placeholder example structure — replace all of this ---
    df = pd.DataFrame()
    df_5m_Price = pd.DataFrame(columns=["Symbol", "LTP", "% Change", "Momentum"])
    df_5m_Vol = pd.DataFrame(columns=["Symbol", "Volume", "% Change", "Momentum"])
    df_opening = pd.DataFrame(columns=["Symbol", "Open", "% Change", "Momentum"])
    # --- end placeholder ---

    return df, df_5m_Price, df_5m_Vol, df_opening


def main():
    now_ist = datetime.now(pytz.utc).astimezone(IST)

    if not is_market_open(now_ist):
        print(f"Market closed at {now_ist.strftime('%H:%M:%S %d%b%y')} IST — skipping run.")
        sys.exit(0)

    df, df_5m_price, df_5m_vol, df_opening = screener()

    timestamp = now_ist.strftime("%Y-%m-%d %H:%M:%S")

    with pd.ExcelWriter("data/live_data.xlsx", engine="openpyxl") as writer:
        (df_5m_price if df_5m_price is not None else pd.DataFrame()).to_excel(
            writer, sheet_name="5m_Price", index=False)
        (df_5m_vol if df_5m_vol is not None else pd.DataFrame()).to_excel(
            writer, sheet_name="5m_Vol", index=False)
        (df_opening if df_opening is not None else pd.DataFrame()).to_excel(
            writer, sheet_name="Opening", index=False)
        pd.DataFrame({"last_updated_ist": [timestamp]}).to_excel(
            writer, sheet_name="meta", index=False)

    print(f"Data written at {timestamp} IST")


if __name__ == "__main__":
    main()
