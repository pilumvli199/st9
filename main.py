from login.angel_login import angel_login
from data.data_fetch import fetch_instruments, fetch_option_chain
from analysis.option_chain_analysis import analyze_option_chain
from alerts.telegram_bot import send_telegram_alert
import schedule
import time


def run_bot():
    obj, data = angel_login()
    if not obj or not data:
        print("❌ Login failed, exiting.")
        return

    # Extract tokens and client id
    client_id = data.get("data", {}).get("clientcode")
    jwt_token = data.get("data", {}).get("jwtToken")
    refresh_token = data.get("data", {}).get("refreshToken")

    # API Key from .env
    import os
    api_key = os.getenv("ANGEL_API_KEY")

    # Fetch instruments
    instruments_df = fetch_instruments()
    if instruments_df.empty:
        print("⚠️ Instruments fetch failed")
        return

    # Filter NIFTY 50 stocks for example
    watchlist = instruments_df[instruments_df["symbol"].isin([
        "TITAN", "ASIANPAINT", "JSWSTEEL", "NTPC", "POWERGRID",
        "GRASIM", "NESTLEIND", "M&M", "INDUSINDBK", "CIPLA",
        "DIVISLAB", "TATACONSUM", "UPL", "DRREDDY", "EICHERMOT",
        "BRITANNIA", "COALINDIA", "SBILIFE", "HINDALCO",
        "ADANIPORTS", "BAJAJFINSV", "HEROMOTOCO", "BPCL",
        "SHREECEM", "TATAMOTORS", "BAJAJ-AUTO", "VEDL", "ICICIPRULI"
    ])]

    for symbol in watchlist["symbol"].unique():
        try:
            option_chain = fetch_option_chain(api_key, client_id, jwt_token, symbol, "26-SEP-2024")
            if option_chain.empty:
                continue

            signals = analyze_option_chain(option_chain)
            if signals:
                send_telegram_alert(f"📊 {symbol}: {signals}")

        except Exception as e:
            print(f"⚠️ Error processing {symbol}: {e}")


if __name__ == "__main__":
    # Run immediately
    run_bot()

    # Schedule every 5 minutes
    schedule.every(5).minutes.do(run_bot)

    while True:
        schedule.run_pending()
        time.sleep(1)
