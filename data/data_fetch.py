import pandas as pd

def fetch_option_chain(obj, symbol, expiry):
    """
    Build option chain manually using instruments master + LTP API.
    obj -> SmartConnect instance (login झाल्यावर मिळालेला)
    symbol -> उदा. 'NIFTY', 'BANKNIFTY'
    expiry -> उदा. '26-SEP-2024'
    """

    try:
        # Get instruments master
        instruments = fetch_instruments()
        if instruments.empty:
            print("⚠️ Instruments not available")
            return pd.DataFrame()

        # Filter contracts for given symbol + expiry
        options = instruments[
            (instruments["name"] == symbol) &
            (instruments["expiry"] == expiry) &
            (instruments["instrumenttype"].isin(["OPTIDX", "OPTSTK"]))
        ].copy()

        if options.empty:
            print(f"⚠️ No options found for {symbol} {expiry}")
            return pd.DataFrame()

        # Fetch LTP for each contract
        chain_data = []
        for _, row in options.iterrows():
            try:
                ltp_resp = obj.ltpData("NSE", row["symbol"], row["token"])
                if "data" in ltp_resp:
                    ltp = ltp_resp["data"].get("ltp", None)
                else:
                    ltp = None

                chain_data.append({
                    "symbol": row["symbol"],
                    "strike": row["strike"],
                    "expiry": row["expiry"],
                    "option_type": row["optiontype"],
                    "ltp": ltp,
                    "token": row["token"]
                })
            except Exception as e:
                print(f"⚠️ LTP fetch failed for {row['symbol']}: {e}")

        return pd.DataFrame(chain_data)

    except Exception as e:
        print(f"⚠️ Option chain fetch error: {e}")
        return pd.DataFrame()

