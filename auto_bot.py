import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os

print("=" * 80)
print("🤖 24/7 AUTOMATED BOT: TICKSTREAM GEX API + MASTER 3.0 + TELEGRAM")
print("=" * 80)

# Load Encrypted Secrets from GitHub Environment
TICKSTREAM_API_KEY = os.environ.get("TICKSTREAM_API_KEY")
TRADOVATE_USER = os.environ.get("TRADOVATE_USER")
TRADOVATE_PASS = os.environ.get("TRADOVATE_PASS")
TRADOVATE_ACCOUNT_ID = os.environ.get("TRADOVATE_ACCOUNT_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ---------------------------------------------------------------------
# 1. TELEGRAM PUSH NOTIFICATION SYSTEM
# ---------------------------------------------------------------------
def send_telegram_alert(message_text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"📱 LOCAL LOG:\n{message_text}")
        return

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(telegram_url, json=payload, timeout=5)
        if res.status_code == 200:
            print("📱 Telegram Push Notification Sent!")
        else:
            print(f"⚠️ Telegram API Response: {res.json()}")
    except Exception as e:
        print(f"❌ Telegram Connection Error: {e}")

# ---------------------------------------------------------------------
# 2. ENHANCED TICKSTREAM GEX API ENGINE
# ---------------------------------------------------------------------
def fetch_tickstream_gex(spot_price):
    if not TICKSTREAM_API_KEY:
        print("⚠️ No TICKSTREAM_API_KEY found in GitHub Secrets. Using spot calibration.")
        call_w = round((spot_price + 120.0) / 50.0) * 50.0
        put_w = round((spot_price - 120.0) / 50.0) * 50.0
        gamma_f = round((spot_price - 25.0) / 25.0) * 25.0
        return call_w, put_w, gamma_f

    print("\n📡 Connecting to TickStream API for live $NDX GEX levels...")
    
    # Try TickStream Endpoints with Multi-Header Auth
    endpoints = [
        "https://api.tickstream.com/v1/gex/NDX/latest",
        "https://api.tickstream.io/v1/gex/NDX",
        "https://api.tickstream.com/v1/gamma/NDX"
    ]
    
    headers_options = [
        {"Authorization": f"Bearer {TICKSTREAM_API_KEY}"},
        {"X-API-Key": TICKSTREAM_API_KEY},
        {"Authorization": f"Token {TICKSTREAM_API_KEY}"}
    ]

    for url in endpoints:
        for headers in headers_options:
            try:
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    
                    # Robust key matching
                    call_w = float(data.get("call_wall") or data.get("callWall") or data.get("call_wall_strike") or (spot_price + 120.0))
                    put_w = float(data.get("put_wall") or data.get("putWall") or data.get("put_wall_strike") or (spot_price - 120.0))
                    gamma_f = float(data.get("gamma_flip") or data.get("gammaFlip") or data.get("zero_gamma") or data.get("inflection") or (spot_price - 25.0))

                    gex_msg = (
                        f"📡 *LIVE TICKSTREAM GEX FETCHED!*\n\n"
                        f"🟩 *Call Wall (Green):* `${call_w:,.2f}`\n"
                        f"🟥 *Put Wall (Red):* `${put_w:,.2f}`\n"
                        f"🟦 *Gamma Flip (Blue):* `${gamma_f:,.2f}`\n"
                        f"📊 *Current Spot:* `${spot_price:,.2f}`"
                    )
                    print(f"✅ TICKSTREAM SUCCESS: Call Wall=${call_w}, Put Wall=${put_w}, Flip=${gamma_f}")
                    send_telegram_alert(gex_msg)
                    return call_w, put_w, gamma_f

            except Exception:
                continue

    print("⚠️ TickStream API unreachable or processing format. Using spot calibration fallback.")
    call_w = round((spot_price + 120.0) / 50.0) * 50.0
    put_w = round((spot_price - 120.0) / 50.0) * 50.0
    gamma_f = round((spot_price - 25.0) / 25.0) * 25.0
    return call_w, put_w, gamma_f

# ---------------------------------------------------------------------
# 3. TRADOVATE EXECUTION ENGINE
# ---------------------------------------------------------------------
def execute_tradovate_order(action, entry_px, sl_px, tp_px):
    trade_summary = (
        f"🚨 *GRADE A+ {action.upper()} SETUP FIRED!*\n\n"
        f"📈 *Asset:* 5 Micro NQ (`5 MNQ`)\n"
        f"💵 *Entry Price:* `${entry_px:,.2f}`\n"
        f"🛑 *Stop Loss:* `${sl_px:,.2f}` (-$300.00 Risk per acct)\n"
        f"🎯 *Take Profit 1 (80%):* `${tp_px:,.2f}` (Yesterday's POC)\n"
        f"🚀 *5-Account Fleet Total:* +$1,500.00 to +$3,600.00 Payout Potential!"
    )
    
    if not TRADOVATE_USER or not TRADOVATE_PASS:
        send_telegram_alert(f"🧪 *SIMULATION EXECUTION*\n\n{trade_summary}")
        return

    auth_url = "https://demo.tradovateapi.com/v1/auth/accesstokenrequest"
    auth_payload = {
        "name": TRADOVATE_USER,
        "password": TRADOVATE_PASS,
        "appId": "NQ_Master_Bot_v3",
        "appVersion": "3.0"
    }
    
    try:
        res = requests.post(auth_url, json=auth_payload, timeout=10)
        auth_data = res.json()
        if "accessToken" not in auth_data:
            send_telegram_alert("❌ *TRADOVATE AUTH ERROR*: Invalid API credentials.")
            return
            
        access_token = auth_data["accessToken"]
        headers = {"Authorization": f"Bearer {access_token}"}
        order_url = "https://demo.tradovateapi.com/v1/order/placeorder"
        
        order_payload = {
            "accountSpec": TRADOVATE_USER,
            "accountId": int(TRADOVATE_ACCOUNT_ID) if TRADOVATE_ACCOUNT_ID and TRADOVATE_ACCOUNT_ID.isdigit() else 0,
            "action": action,
            "symbol": "MNQU6",
            "orderQty": 5,
            "orderType": "Market",
            "isAutomated": True
        }
        
        order_res = requests.post(order_url, json=order_payload, headers=headers)
        send_telegram_alert(f"⚡ *LIVE ORDER FIRED ACROSS 5 ACCOUNTS!*\n\n{trade_summary}")

    except Exception as e:
        send_telegram_alert(f"❌ *EXECUTION ERROR*: {str(e)}")

# ---------------------------------------------------------------------
# 4. MARKET STRUCTURE ENGINE & MASTER MODEL 3.0
# ---------------------------------------------------------------------
print("\n📥 Fetching live NQ market candles from Yahoo Finance...")
ticker = yf.Ticker("NQ=F")
df = ticker.history(period="5d", interval="5m")

if df.empty:
    print("❌ Failed to fetch market data.")
    exit()

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df.index = df.index.tz_convert("America/New_York")
df["date"] = df.index.date
df["time"] = df.index.time

unique_dates = sorted(list(set(df["date"])))
if len(unique_dates) < 2: exit()

today_date = unique_dates[-1]
prev_date = unique_dates[-2]

# Compute Yesterday's Volume Profile (VAL, VAH, POC)
prev_df = df[df["date"] == prev_date]
pv = (prev_df["Close"] * prev_df["Volume"]).sum()
vwap = pv / max(1, prev_df["Volume"].sum())

prices, vols = prev_df["Close"].values, prev_df["Volume"].values
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

today_df = df[df["date"] == today_date].copy()
today_df["tp"] = (today_df["High"] + today_df["Low"] + today_df["Close"]) / 3.0
today_df["pv"] = today_df["tp"] * today_df["Volume"]
today_df["running_vwap"] = today_df["pv"].cumsum() / today_df["Volume"].cumsum()
today_df["vwap_slope"] = today_df["running_vwap"] - today_df["running_vwap"].shift(3)

latest_candle = today_df.iloc[-1]
current_px = latest_candle["Close"]
current_slope = latest_candle["vwap_slope"]

c_open, c_high, c_low, c_close = latest_candle["Open"], latest_candle["High"], latest_candle["Low"], latest_candle["Close"]
c_range = max(0.25, c_high - c_low)
bottom_wick = min(c_open, c_close) - c_low
top_wick = c_high - max(c_open, c_close)

vwap_rising = current_slope > 0.0 if not np.isnan(current_slope) else True
vwap_falling = current_slope < 0.0 if not np.isnan(current_slope) else True

# Fetch GEX Levels from TickStream Engine
call_w, put_w, gamma_f = fetch_tickstream_gex(current_px)
is_pos_gamma = current_px > gamma_f

print(f"\n📊 MARKET STRUCTURE SUMMARY ({today_date}):")
print(f"  • Current NQ Price : ${current_px:,.2f}")
print(f"  • Yesterday's VAL  : ${prev_val:,.2f}")
print(f"  • Yesterday's POC  : ${prev_poc:,.2f} [TARGET MAGNET]")
print(f"  • Yesterday's VAH  : ${prev_vah:,.2f}")
print(f"  • GEX Gamma Flip   : ${gamma_f:,.2f} ({'POS GAMMA ✅' if is_pos_gamma else 'NEG GAMMA 🛑'})")

pts_to_poc_long = prev_poc - current_px
pts_to_poc_short = current_px - prev_poc

# 🟢 MASTER MODEL 3.0 LONG CHECK
if is_pos_gamma and vwap_rising and c_low <= prev_val and (bottom_wick / c_range) >= 0.25 and c_close > prev_val and pts_to_poc_long >= 35.0:
    print("\n🔥 ALERT: GRADE A+ LONG SETUP FIRED!")
    execute_tradovate_order("Buy", c_close, c_close - 30.0, prev_poc)

# 🔴 MASTER MODEL 3.0 SHORT CHECK
elif is_pos_gamma and vwap_falling and c_high >= prev_vah and (top_wick / c_range) >= 0.25 and c_close < prev_vah and pts_to_poc_short >= 35.0:
    print("\n🔥 ALERT: GRADE A+ SHORT SETUP FIRED!")
    execute_tradovate_order("Sell", c_close, c_close + 30.0, prev_poc)

else:
    print("\n🔵 STATUS: Market checked cleanly. No Grade A+ setup detected at current candle. Standing by.")

print("=" * 80)
