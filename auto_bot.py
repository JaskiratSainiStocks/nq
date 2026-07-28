import yfinance as yf
import pandas as pd
import numpy as np

print("=" * 75)
print("🤖 AUTOMATED PRE-SCHOOL BOT: EXECUTING MASTER MODEL 3.0")
print("=" * 75)

# Fetch latest intraday NQ futures data
print("\n📥 Fetching live NQ market structure from Yahoo Finance...")
ticker = yf.Ticker("NQ=F")
df = ticker.history(period="5d", interval="5m")

if df.empty:
    print("❌ Failed to fetch market data.")
    exit()

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Convert timezone to EST
df.index = df.index.tz_convert("America/New_York")
df["date"] = df.index.date
df["time"] = df.index.time

unique_dates = sorted(list(set(df["date"])))
if len(unique_dates) < 2:
    print("❌ Not enough days to compute yesterday's profile.")
    exit()

today_date = unique_dates[-1]
prev_date = unique_dates[-2]

# 1. Compute Yesterday's Volume Profile (VAL, VAH, POC)
prev_df = df[df["date"] == prev_date]
pv = (prev_df["Close"] * prev_df["Volume"]).sum()
vwap = pv / max(1, prev_df["Volume"].sum())

prices = prev_df["Close"].values
vols = prev_df["Volume"].values
poc_idx = np.argmax(vols)
prev_poc = prices[poc_idx]

target_va_vol = prev_df["Volume"].sum() * 0.6827
va_vol = vols[poc_idx]
up = dn = poc_idx
while va_vol < target_va_vol and (up < len(prices) - 1 or dn > 0):
    next_up = vols[up + 1] if up < len(prices) - 1 else 0
    next_dn = vols[dn - 1] if dn > 0 else 0
    if next_up >= next_dn: up += 1; va_vol += next_up
    else: dn -= 1; va_vol += next_dn

prev_vah, prev_val = prices[up], prices[dn]

print(f"📅 Today's Date  : {today_date}")
print(f"📊 Previous VAL  : ${prev_val:,.2f} [LONG RECLAIM ZONE]")
print(f"📊 Previous POC  : ${prev_poc:,.2f} [TARGET MAGNET]")
print(f"📊 Previous VAH  : ${prev_vah:,.2f} [SHORT REJECTION ZONE]")

# 2. Check Today's Morning Candle at 09:35 AM EST (06:35 AM PST)
today_df = df[df["date"] == today_date].copy()
today_df["tp"] = (today_df["High"] + today_df["Low"] + today_df["Close"]) / 3.0
today_df["pv"] = today_df["tp"] * today_df["Volume"]
today_df["running_vwap"] = today_df["pv"].cumsum() / today_df["Volume"].cumsum()
today_df["vwap_slope"] = today_df["running_vwap"] - today_df["running_vwap"].shift(3)

latest_candle = today_df.iloc[-1]
current_px = latest_candle["Close"]
current_vwap = latest_candle["running_vwap"]
current_slope = latest_candle["vwap_slope"]

c_open, c_high, c_low, c_close = latest_candle["Open"], latest_candle["High"], latest_candle["Low"], latest_candle["Close"]
c_range = max(0.25, c_high - c_low)
bottom_wick = min(c_open, c_close) - c_low
top_wick = c_high - max(c_open, c_close)

vwap_rising = current_slope > 0.0 if not np.isnan(current_slope) else True
vwap_falling = current_slope < 0.0 if not np.isnan(current_slope) else True

print(f"\n🔍 Current NQ Price: ${current_px:,.2f} | Running VWAP: ${current_vwap:,.2f}")

# 3. Evaluate Master Model 3.0 Triggers
pts_to_poc_long = prev_poc - current_px
pts_to_poc_short = current_px - prev_poc

# 🟢 LONG CHECK
if vwap_rising and c_low <= prev_val and (bottom_wick / c_range) >= 0.25 and c_close > prev_val and pts_to_poc_long >= 35.0:
    print("\n🔥 ALERT: GRADE A+ LONG SETUP FIRED!")
    print(f"  • Entry Order    : BUY 5 Micro NQ (5 MNQ) at ${c_close:,.2f}")
    print(f"  • Stop Loss      : ${c_close - 30.0:,.2f} (-30 Points / -$300.00)")
    print(f"  • Target 1 (80%) : ${prev_poc:,.2f} (Yesterday's POC / +{pts_to_poc_long:.1f} pts)")
    print(f"  • Target 2 (20%) : ${prev_vah:,.2f} (Yesterday's VAH Runner)")

# 🔴 SHORT CHECK
elif vwap_falling and c_high >= prev_vah and (top_wick / c_range) >= 0.25 and c_close < prev_vah and pts_to_poc_short >= 35.0:
    print("\n🔥 ALERT: GRADE A+ SHORT SETUP FIRED!")
    print(f"  • Entry Order    : SHORT 5 Micro NQ (5 MNQ) at ${c_close:,.2f}")
    print(f"  • Stop Loss      : ${c_close + 30.0:,.2f} (-30 Points / -$300.00)")
    print(f"  • Target 1 (80%) : ${prev_poc:,.2f} (Yesterday's POC / +{pts_to_poc_short:.1f} pts)")
    print(f"  • Target 2 (20%) : ${prev_val:,.2f} (Yesterday's VAL Runner)")

else:
    print("\n🔵 STATUS: No Grade A+ setup detected at current candle. Standing by.")

print("=" * 75)
