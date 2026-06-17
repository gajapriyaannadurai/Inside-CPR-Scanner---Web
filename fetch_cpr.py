"""
fetch_cpr.py
------------
Runs automatically via GitHub Actions every weekday at 3:45 PM IST.
Fetches OHLC from Yahoo Finance for all NSE stocks,
calculates Inside CPR / Virgin CPR / CPR Trend,
and saves the result as cpr_data.json in the repo.

Stark School of Finance — tradingwithgp.com
"""

import json
import time
import datetime
import yfinance as yf
from pathlib import Path

# ─── Stock universe ────────────────────────────────────────────────────────────
STOCKS = [
    # symbol, name, sector, fno(bool)
    ("RELIANCE",    "Reliance Industries",          "Oil & Gas",            True),
    ("TCS",         "Tata Consultancy Services",    "Information Technology",True),
    ("HDFCBANK",    "HDFC Bank",                    "Financial Services",   True),
    ("BHARTIARTL",  "Bharti Airtel",                "Telecom",              True),
    ("ICICIBANK",   "ICICI Bank",                   "Financial Services",   True),
    ("INFY",        "Infosys",                      "Information Technology",True),
    ("SBIN",        "State Bank of India",          "Financial Services",   True),
    ("HINDUNILVR",  "Hindustan Unilever",           "FMCG",                 True),
    ("ITC",         "ITC",                          "FMCG",                 True),
    ("KOTAKBANK",   "Kotak Mahindra Bank",          "Financial Services",   True),
    ("LT",          "Larsen & Toubro",              "Capital Goods",        True),
    ("AXISBANK",    "Axis Bank",                    "Financial Services",   True),
    ("BAJFINANCE",  "Bajaj Finance",                "Financial Services",   True),
    ("MARUTI",      "Maruti Suzuki",                "Automobile",           True),
    ("ASIANPAINT",  "Asian Paints",                 "Consumer Durables",    True),
    ("TITAN",       "Titan Company",                "Consumer Durables",    True),
    ("SUNPHARMA",   "Sun Pharmaceutical",           "Healthcare",           True),
    ("NESTLEIND",   "Nestle India",                 "FMCG",                 True),
    ("TATAMOTORS",  "Tata Motors",                  "Automobile",           True),
    ("WIPRO",       "Wipro",                        "Information Technology",True),
    ("ONGC",        "ONGC",                         "Oil & Gas",            True),
    ("NTPC",        "NTPC",                         "Power",                True),
    ("POWERGRID",   "Power Grid Corp",              "Power",                True),
    ("TATASTEEL",   "Tata Steel",                   "Metals & Mining",      True),
    ("TECHM",       "Tech Mahindra",                "Information Technology",True),
    ("HCLTECH",     "HCL Technologies",             "Information Technology",True),
    ("DRREDDY",     "Dr. Reddy's Labs",             "Healthcare",           True),
    ("DIVISLAB",    "Divi's Laboratories",          "Healthcare",           True),
    ("JSWSTEEL",    "JSW Steel",                    "Metals & Mining",      True),
    ("ADANIENT",    "Adani Enterprises",            "Metals & Mining",      True),
    ("BAJAJFINSV",  "Bajaj Finserv",                "Financial Services",   True),
    ("ULTRACEMCO",  "UltraTech Cement",             "Construction Materials",True),
    ("GRASIM",      "Grasim Industries",            "Construction Materials",True),
    ("INDUSINDBK",  "IndusInd Bank",                "Financial Services",   True),
    ("CIPLA",       "Cipla",                        "Healthcare",           True),
    ("EICHERMOT",   "Eicher Motors",                "Automobile",           True),
    ("APOLLOHOSP",  "Apollo Hospitals",             "Healthcare",           True),
    ("BPCL",        "BPCL",                         "Oil & Gas",            True),
    ("COALINDIA",   "Coal India",                   "Oil & Gas",            True),
    ("BRITANNIA",   "Britannia Industries",         "FMCG",                 True),
    ("TATACONSUM",  "Tata Consumer Products",       "FMCG",                 True),
    ("HEROMOTOCO",  "Hero MotoCorp",                "Automobile",           True),
    ("HINDALCO",    "Hindalco Industries",          "Metals & Mining",      True),
    ("SBILIFE",     "SBI Life Insurance",           "Financial Services",   True),
    ("HDFCLIFE",    "HDFC Life Insurance",          "Financial Services",   True),
    ("BAJAJ-AUTO",  "Bajaj Auto",                   "Automobile",           True),
    ("M&M",         "Mahindra & Mahindra",          "Automobile",           True),
    ("SHRIRAMFIN",  "Shriram Finance",              "Financial Services",   True),
    ("TRENT",       "Trent",                        "Consumer Services",    True),
    ("BEL",         "Bharat Electronics",           "Capital Goods",        True),
    # Nifty Bank extra
    ("BANDHANBNK",  "Bandhan Bank",                 "Financial Services",   True),
    ("FEDERALBNK",  "Federal Bank",                 "Financial Services",   True),
    ("IDFCFIRSTB",  "IDFC First Bank",              "Financial Services",   True),
    ("AUBANK",      "AU Small Finance Bank",        "Financial Services",   True),
    ("PNB",         "Punjab National Bank",         "Financial Services",   True),
    ("BANKBARODA",  "Bank of Baroda",               "Financial Services",   True),
    # Nifty IT extra
    ("LTIM",        "LTIMindtree",                  "Information Technology",True),
    ("MPHASIS",     "Mphasis",                      "Information Technology",True),
    ("COFORGE",     "Coforge",                      "Information Technology",True),
    ("PERSISTENT",  "Persistent Systems",           "Information Technology",True),
    ("OFSS",        "Oracle Financial Services",    "Information Technology",True),
    ("LTTS",        "L&T Technology Services",      "Information Technology",True),
    # Nifty 100 / 200 extra
    ("ADANIPORTS",  "Adani Ports",                  "Services",             True),
    ("ADANIPOWER",  "Adani Power",                  "Power",                True),
    ("ADANIGREEN",  "Adani Green Energy",           "Power",                True),
    ("HAL",         "Hindustan Aeronautics",        "Capital Goods",        True),
    ("RVNL",        "Rail Vikas Nigam",             "Capital Goods",        True),
    ("IRFC",        "Indian Railway Finance",       "Financial Services",   True),
    ("NHPC",        "NHPC",                         "Power",                True),
    ("RECLTD",      "REC",                          "Financial Services",   True),
    ("PFC",         "Power Finance Corp",           "Financial Services",   True),
    ("ZOMATO",      "Zomato",                       "Consumer Services",    True),
    ("JIOFINANCE",  "Jio Financial Services",       "Financial Services",   True),
    ("NYKAA",       "FSN E-Commerce (Nykaa)",       "Consumer Services",    True),
    ("DMART",       "Avenue Supermarts",            "Consumer Services",    True),
    ("IRCTC",       "IRCTC",                        "Services",             True),
    ("NAUKRI",      "Info Edge (Naukri)",           "Services",             True),
    ("HDFCAMC",     "HDFC AMC",                     "Financial Services",   True),
    ("ICICIGI",     "ICICI Lombard",                "Financial Services",   True),
    ("ICICIPRULI",  "ICICI Prudential Life",        "Financial Services",   True),
    ("SBICARD",     "SBI Cards",                    "Financial Services",   True),
    ("STARHEALTH",  "Star Health Insurance",        "Financial Services",   True),
    ("MFSL",        "Max Financial Services",       "Financial Services",   True),
    ("GAIL",        "GAIL India",                   "Oil & Gas",            True),
    ("IOC",         "Indian Oil Corporation",       "Oil & Gas",            True),
    ("HINDPETRO",   "Hindustan Petroleum",          "Oil & Gas",            True),
    ("HINDCOPPER",  "Hindustan Copper",             "Metals & Mining",      True),
    ("HINDZINC",    "Hindustan Zinc",               "Metals & Mining",      True),
    ("NMDC",        "NMDC",                         "Metals & Mining",      True),
    ("SAIL",        "Steel Authority of India",     "Metals & Mining",      True),
    ("VEDL",        "Vedanta",                      "Metals & Mining",      True),
    ("JINDALSTEL",  "Jindal Steel & Power",         "Metals & Mining",      True),
    ("NATIONALUM",  "National Aluminium",           "Metals & Mining",      True),
    ("DABUR",       "Dabur India",                  "FMCG",                 True),
    ("MARICO",      "Marico",                       "FMCG",                 True),
    ("COLPAL",      "Colgate Palmolive",            "FMCG",                 True),
    ("GODREJCP",    "Godrej Consumer Products",     "FMCG",                 True),
    ("TATAPOWER",   "Tata Power",                   "Power",                True),
    ("TATACHEM",    "Tata Chemicals",               "Chemicals",            True),
    ("TATACOMM",    "Tata Communications",          "Telecom",              True),
    ("TATAELXSI",   "Tata Elxsi",                   "Information Technology",False),
    ("LUPIN",       "Lupin",                        "Healthcare",           True),
    ("TORNTPHARM",  "Torrent Pharmaceuticals",      "Healthcare",           True),
    ("ZYDUSLIFE",   "Zydus Lifesciences",           "Healthcare",           True),
    ("SYNGENE",     "Syngene International",        "Healthcare",           True),
    ("GLAND",       "Gland Pharma",                 "Healthcare",           True),
    ("FORTIS",      "Fortis Healthcare",            "Healthcare",           True),
    ("BIOCON",      "Biocon",                       "Healthcare",           True),
    ("AUROPHARMA",  "Aurobindo Pharma",             "Healthcare",           True),
    ("DLF",         "DLF",                          "Realty",               True),
    ("GODREJPROP",  "Godrej Properties",            "Realty",               True),
    ("DALBHARAT",   "Dalmia Bharat",                "Construction Materials",True),
    ("SHREECEM",    "Shree Cement",                 "Construction Materials",True),
    ("AMBUJACEM",   "Ambuja Cements",               "Construction Materials",True),
    ("ACC",         "ACC",                          "Construction Materials",True),
    ("SIEMENS",     "Siemens",                      "Capital Goods",        True),
    ("ABB",         "ABB India",                    "Capital Goods",        True),
    ("POLYCAB",     "Polycab India",                "Capital Goods",        True),
    ("BHEL",        "BHEL",                         "Capital Goods",        True),
    ("CUMMINSIND",  "Cummins India",                "Capital Goods",        True),
    ("ASHOKLEY",    "Ashok Leyland",                "Capital Goods",        True),
    ("ESCORTS",     "Escorts Kubota",               "Capital Goods",        True),
    ("BHARATFORG",  "Bharat Forge",                 "Automobile",           True),
    ("BALKRISIND",  "Balkrishna Industries",        "Automobile",           True),
    ("APOLLOTYRE",  "Apollo Tyres",                 "Automobile",           True),
    ("MRF",         "MRF",                          "Automobile",           True),
    ("TVSMOTOR",    "TVS Motor",                    "Automobile",           True),
    ("BOSCHLTD",    "Bosch",                        "Automobile",           True),
    ("MUTHOOTFIN",  "Muthoot Finance",              "Financial Services",   True),
    ("MANAPPURAM",  "Manappuram Finance",           "Financial Services",   True),
    ("CHOLAFIN",    "Cholamandalam Finance",        "Financial Services",   True),
    ("L&TFH",       "L&T Finance",                  "Financial Services",   True),
    ("M&MFIN",      "Mahindra Finance",             "Financial Services",   True),
    ("CANBK",       "Canara Bank",                  "Financial Services",   True),
    ("BANKINDIA",   "Bank of India",                "Financial Services",   True),
    ("UNIONBANK",   "Union Bank of India",          "Financial Services",   True),
    ("IEX",         "India Energy Exchange",        "Financial Services",   True),
    ("MCX",         "MCX",                          "Financial Services",   True),
    ("BSE",         "BSE",                          "Financial Services",   True),
    ("CDSL",        "CDSL",                         "Financial Services",   True),
    ("ANGELONE",    "Angel One",                    "Financial Services",   True),
    ("RBLBANK",     "RBL Bank",                     "Financial Services",   True),
    ("SRF",         "SRF",                          "Chemicals",            True),
    ("DEEPAKNTR",   "Deepak Nitrite",               "Chemicals",            True),
    ("PIIND",       "PI Industries",                "Chemicals",            True),
    ("FLUOROCHEM",  "Gujarat Fluorochemicals",      "Chemicals",            True),
    ("AARTIIND",    "Aarti Industries",             "Chemicals",            True),
    ("UPL",         "UPL",                          "Chemicals",            True),
    ("DIXON",       "Dixon Technologies",           "Consumer Durables",    True),
    ("VOLTAS",      "Voltas",                       "Consumer Durables",    True),
    ("CROMPTON",    "Crompton Greaves",             "Consumer Durables",    True),
    ("PAGEIND",     "Page Industries",              "Consumer Durables",    True),
    ("KAJARIACER",  "Kajaria Ceramics",             "Consumer Durables",    True),
    ("INDIAMART",   "IndiaMART InterMESH",          "Services",             True),
    ("CONCOR",      "Container Corporation",        "Services",             True),
    ("INDUSTOWER",  "Indus Towers",                 "Telecom",              True),
    ("MGL",         "Mahanagar Gas",                "Oil & Gas",            True),
    ("PETRONET",    "Petronet LNG",                 "Oil & Gas",            True),
    ("GSPL",        "Gujarat State Petronet",       "Oil & Gas",            True),
    ("JUBLFOOD",    "Jubilant FoodWorks",           "Consumer Services",    True),
    ("INDHOTEL",    "Indian Hotels",                "Consumer Services",    True),
    ("CYIENT",      "Cyient",                       "Information Technology",True),
    ("INTELLECT",   "Intellect Design Arena",       "Information Technology",True),
    ("LAURUSLABS",  "Laurus Labs",                  "Healthcare",           True),
    ("LALPATHLAB",  "Dr Lal PathLabs",              "Healthcare",           False),
    ("CGPOWER",     "CG Power",                     "Capital Goods",        True),
    ("ASTRAL",      "Astral",                       "Capital Goods",        True),
    ("COROMANDEL",  "Coromandel International",     "Chemicals",            True),
    ("CANFINHOME",  "Can Fin Homes",                "Financial Services",   True),
    ("CAMS",        "CAMS",                         "Financial Services",   True),
    ("ABCAPITAL",   "Aditya Birla Capital",         "Financial Services",   True),
    ("ALKYLAMINE",  "Alkyl Amines Chemicals",       "Chemicals",            True),
    ("APLAPOLLO",   "APL Apollo Tubes",             "Capital Goods",        True),
    ("AMBER",       "Amber Enterprises",            "Consumer Durables",    True),
    ("KFIN",        "KFin Technologies",            "Financial Services",   True),
    ("360ONE",      "360 ONE WAM",                  "Financial Services",   True),
    ("SJVN",        "SJVN",                         "Power",                False),
    ("HUDCO",       "HUDCO",                        "Financial Services",   False),
    ("GRSE",        "Garden Reach Shipbuilders",    "Capital Goods",        False),
    ("BDL",         "Bharat Dynamics",              "Capital Goods",        True),
    ("RAMCOCEM",    "Ramco Cements",                "Construction Materials",True),
    ("SUNTV",       "Sun TV Network",               "Consumer Services",    False),
    ("TORNTPOWER",  "Torrent Power",                "Power",                False),
    ("JSWENERGY",   "JSW Energy",                   "Power",                False),
    ("CESC",        "CESC",                         "Power",                False),
    ("HAVELLS",     "Havells India",                "Consumer Durables",    False),
    ("BERGEPAINT",  "Berger Paints",                "Consumer Durables",    True),
    ("ALKEM",       "Alkem Laboratories",           "Healthcare",           True),
    ("IPCALAB",     "IPCA Laboratories",            "Healthcare",           False),
    ("NATCOPHARM",  "Natco Pharma",                 "Healthcare",           False),
    ("METROPOLIS",  "Metropolis Healthcare",        "Healthcare",           False),
    ("MAXHEALTH",   "Max Healthcare",               "Healthcare",           False),
    ("ASTERDM",     "Aster DM Healthcare",          "Healthcare",           False),
    ("SUZLON",      "Suzlon Energy",                "Power",                False),
    ("YESBANK",     "Yes Bank",                     "Financial Services",   False),
    ("OBEROIRLTY",  "Oberoi Realty",                "Realty",               False),
    ("PRESTIGE",    "Prestige Estates",             "Realty",               False),
    ("BRIGADE",     "Brigade Enterprises",          "Realty",               False),
    ("HAPPSTMNDS",  "Happiest Minds",               "Information Technology",False),
    ("KPITTECH",    "KPIT Technologies",            "Information Technology",False),
    ("MAPMYINDIA",  "MapMyIndia",                   "Information Technology",False),
    ("HONASA",      "Honasa Consumer",              "FMCG",                 False),
    ("BIKAJI",      "Bikaji Foods",                 "FMCG",                 False),
    ("DEVYANI",     "Devyani International",        "Consumer Services",    False),
    ("KALYANKJIL",  "Kalyan Jewellers",             "Consumer Durables",    False),
    ("CENTURYPLY",  "Century Plyboards",            "Consumer Durables",    False),
    ("CLEAN",       "Clean Science",                "Chemicals",            False),
    ("DEEPAKFERT",  "Deepak Fertilisers",           "Chemicals",            False),
    ("CHAMBLFERT",  "Chambal Fertilizers",          "Chemicals",            False),
    ("GNFC",        "Gujarat Narmada Fertilizers",  "Chemicals",            False),
    ("IIFL",        "IIFL Finance",                 "Financial Services",   False),
    ("CREDITACC",   "CreditAccess Grameen",         "Financial Services",   False),
    ("FIVESTAR",    "Five-Star Business Finance",   "Financial Services",   False),
    ("SUNDARMFIN",  "Sundaram Finance",             "Financial Services",   False),
    ("LICHSGFIN",   "LIC Housing Finance",          "Financial Services",   False),
    ("PNBHOUSING",  "PNB Housing Finance",          "Financial Services",   False),
    ("GICRE",       "General Insurance Corp",       "Financial Services",   False),
    ("DELHIVERY",   "Delhivery",                    "Services",             False),
    ("FSL",         "Firstsource Solutions",        "Services",             False),
    ("COCHINSHIP",  "Cochin Shipyard",              "Capital Goods",        False),
    ("AETHER",      "Aether Industries",            "Chemicals",            False),
    ("HSCL",        "Himadri Speciality Chemical",  "Chemicals",            False),
    ("NAVINFLUOR",  "Navin Fluorine",               "Chemicals",            False),
    ("DCMSHRIRAM",  "DCM Shriram",                  "Diversified",          False),
    ("GODREJIND",   "Godrej Industries",            "Diversified",          False),
]

# ─── CPR calculation ──────────────────────────────────────────────────────────
def calc_cpr(h, l, c):
    pivot = (h + l + c) / 3
    tc    = (pivot + h) / 2
    bc    = (pivot + l) / 2
    return {"pivot": round(pivot, 2), "tc": round(tc, 2), "bc": round(bc, 2)}

def is_inside_cpr(curr, prev):
    curr_w = curr["tc"] - curr["bc"]
    prev_w = prev["tc"] - prev["bc"]
    return (
        curr["tc"] < prev["tc"] and
        curr["bc"] > prev["bc"] and
        curr_w < prev_w
    )

def cpr_width_pct(cpr, price):
    return round(((cpr["tc"] - cpr["bc"]) / price) * 100, 3)

def cpr_trend(pivots):
    """Returns bullish/bearish/sideways based on last 5 pivot direction."""
    up = sum(1 for i in range(1, len(pivots)) if pivots[i] > pivots[i-1])
    dn = sum(1 for i in range(1, len(pivots)) if pivots[i] < pivots[i-1])
    if up >= 3: return "bullish"
    if dn >= 3: return "bearish"
    return "sideways"

# ─── Fetch OHLC from Yahoo Finance ──────────────────────────────────────────
# ─── Yahoo Finance symbol overrides ──────────────────────────────────────────
# Some NSE symbols differ from Yahoo Finance tickers
YAHOO_SYMBOL_MAP = {
    "M&M":         "M%26M.NS",
    "M&MFIN":      "M%26MFIN.NS",
    "L&TFH":       "LTFH.NS",
    "BAJAJ-AUTO":  "BAJAJ-AUTO.NS",
    "JIOFINANCE":  "JIOFIN.NS",
    "LTIM":        "LTIM.NS",
    "ZOMATO":      "ZOMATO.NS",
    "TATAMOTORS":  "TATAMOTORS.NS",
    "360ONE":      "360ONE.NS",
    "NYKAA":       "NYKAA.NS",
    "DMART":       "DMART.NS",
    "PVRINOX":     "PVRINOX.NS",
    "ABFRL":       "ABFRL.NS",
    "ATGL":        "ATGL.NS",
    "AWL":         "AWL.NS",
    "RVNL":        "RVNL.NS",
    "IRFC":        "IRFC.NS",
    "KFIN":        "KFIN.NS",
    "AMBER":       "AMBER.NS",
    "HONASA":      "HONASA.NS",
    "JSWINFRA":    "JSWINFRA.NS",
    "SWIGGY":      "SWIGGY.NS",
}

def get_yahoo_ticker(symbol):
    """Return the correct Yahoo Finance ticker for a given NSE symbol."""
    if symbol in YAHOO_SYMBOL_MAP:
        return YAHOO_SYMBOL_MAP[symbol]
    return symbol + ".NS"

def fetch_stock(symbol):
    """Fetch last 10 daily, 3 monthly weekly, 2 years monthly candles."""
    try:
        yahoo_sym = get_yahoo_ticker(symbol)
        ticker = yf.Ticker(yahoo_sym)
        # Fetch enough history for all 3 timeframes
        hist = ticker.history(period="2y", interval="1d", auto_adjust=True)
        if hist.empty or len(hist) < 3:
            return None

        # Filter complete candles only (no today's live candle)
        hist = hist.dropna(subset=["High", "Low", "Close"])

        # ── Daily bars (last 3 complete trading days) ──
        daily = hist.tail(3)
        if len(daily) < 3:
            return None

        d_curr = {"h": daily.iloc[-1]["High"], "l": daily.iloc[-1]["Low"], "c": daily.iloc[-1]["Close"]}
        d_prev = {"h": daily.iloc[-2]["High"], "l": daily.iloc[-2]["Low"], "c": daily.iloc[-2]["Close"]}
        price  = round(float(d_curr["c"]), 2)
        volume = int(daily.iloc[-1]["Volume"]) if "Volume" in daily.columns else 0
        chg    = round(((d_curr["c"] - d_prev["c"]) / d_prev["c"]) * 100, 2)

        # ── Weekly bars ──
        hist_wk = yf.Ticker(yahoo_sym).history(period="3mo", interval="1wk", auto_adjust=True).dropna(subset=["High","Low","Close"])
        w_curr = w_prev = None
        if len(hist_wk) >= 2:
            w_curr = {"h": hist_wk.iloc[-1]["High"], "l": hist_wk.iloc[-1]["Low"], "c": hist_wk.iloc[-1]["Close"]}
            w_prev = {"h": hist_wk.iloc[-2]["High"], "l": hist_wk.iloc[-2]["Low"], "c": hist_wk.iloc[-2]["Close"]}

        # ── Monthly bars ──
        hist_mo = yf.Ticker(yahoo_sym).history(period="2y", interval="1mo", auto_adjust=True).dropna(subset=["High","Low","Close"])
        m_curr = m_prev = None
        if len(hist_mo) >= 2:
            m_curr = {"h": hist_mo.iloc[-1]["High"], "l": hist_mo.iloc[-1]["Low"], "c": hist_mo.iloc[-1]["Close"]}
            m_prev = {"h": hist_mo.iloc[-2]["High"], "l": hist_mo.iloc[-2]["Low"], "c": hist_mo.iloc[-2]["Close"]}

        # ── CPR trend: last 5 daily pivots ──
        last5 = hist.tail(5)
        pivots = [round((row["High"]+row["Low"]+row["Close"])/3, 2) for _, row in last5.iterrows()]

        return {
            "symbol": symbol,
            "price": price,
            "change": chg,
            "volume": volume,
            "daily":   {"curr": d_curr, "prev": d_prev},
            "weekly":  {"curr": w_curr, "prev": w_prev} if w_curr else None,
            "monthly": {"curr": m_curr, "prev": m_prev} if m_curr else None,
            "pivots5": pivots,
        }
    except Exception as e:
        print(f"  ERROR {symbol} ({get_yahoo_ticker(symbol)}): {e}")
        return None

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print(f"Starting CPR scan — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"Total stocks: {len(STOCKS)}")

    output = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST"),
        "generated_date": datetime.datetime.now().strftime("%d %b %Y"),
        "total_stocks": len(STOCKS),
        "stocks": []
    }

    failed = 0
    for i, (sym, name, sector, fno) in enumerate(STOCKS):
        print(f"  [{i+1}/{len(STOCKS)}] {sym}...", end=" ")
        data = fetch_stock(sym)
        if not data:
            print("SKIP")
            failed += 1
            time.sleep(0.3)
            continue

        # ── Calculate CPR for all timeframes ──
        stock_entry = {
            "symbol":  sym,
            "name":    name,
            "sector":  sector,
            "fno":     fno,
            "price":   data["price"],
            "change":  data["change"],
            "volume":  data["volume"],
        }

        # Daily CPR
        dc = calc_cpr(data["daily"]["curr"]["h"], data["daily"]["curr"]["l"], data["daily"]["curr"]["c"])
        dp = calc_cpr(data["daily"]["prev"]["h"], data["daily"]["prev"]["l"], data["daily"]["prev"]["c"])
        stock_entry["daily"] = {
            "curr_cpr": dc,
            "prev_cpr": dp,
            "inside":   is_inside_cpr(dc, dp),
            "width_pct": cpr_width_pct(dc, data["price"]),
            "trend":    "bullish" if data["price"] > dc["pivot"] else "bearish",
        }

        # Weekly CPR
        if data["weekly"]:
            wc = calc_cpr(data["weekly"]["curr"]["h"], data["weekly"]["curr"]["l"], data["weekly"]["curr"]["c"])
            wp = calc_cpr(data["weekly"]["prev"]["h"], data["weekly"]["prev"]["l"], data["weekly"]["prev"]["c"])
            stock_entry["weekly"] = {
                "curr_cpr": wc,
                "prev_cpr": wp,
                "inside":   is_inside_cpr(wc, wp),
                "width_pct": cpr_width_pct(wc, data["price"]),
                "trend":    "bullish" if data["price"] > wc["pivot"] else "bearish",
            }

        # Monthly CPR
        if data["monthly"]:
            mc = calc_cpr(data["monthly"]["curr"]["h"], data["monthly"]["curr"]["l"], data["monthly"]["curr"]["c"])
            mp = calc_cpr(data["monthly"]["prev"]["h"], data["monthly"]["prev"]["l"], data["monthly"]["prev"]["c"])
            stock_entry["monthly"] = {
                "curr_cpr": mc,
                "prev_cpr": mp,
                "inside":   is_inside_cpr(mc, mp),
                "width_pct": cpr_width_pct(mc, data["price"]),
                "trend":    "bullish" if data["price"] > mc["pivot"] else "bearish",
            }

        # CPR Trend (5-day pivot direction)
        pivots = data["pivots5"]
        stock_entry["cpr_trend"] = {
            "direction": cpr_trend(pivots),
            "pivots":    pivots,
            "pivot_shift": round(pivots[-1] - pivots[0], 2) if len(pivots) >= 2 else 0,
        }

        # Virgin CPR — price has not touched CPR zone today
        # (approximated: if price is more than 0.5% away from CPR zone)
        dist_to_cpr = min(
            abs(data["price"] - dc["tc"]),
            abs(data["price"] - dc["bc"])
        )
        in_cpr_zone = dc["bc"] <= data["price"] <= dc["tc"]
        stock_entry["virgin_cpr"] = {
            "is_virgin": not in_cpr_zone,
            "position":  "above" if data["price"] > dc["tc"] else ("below" if data["price"] < dc["bc"] else "inside"),
            "dist_pct":  round((dist_to_cpr / data["price"]) * 100, 2),
        }

        output["stocks"].append(stock_entry)
        print(f"OK — Inside(D):{stock_entry['daily']['inside']} Price:₹{data['price']}")
        time.sleep(0.4)  # Be polite to Yahoo Finance

    output["success_count"] = len(output["stocks"])
    output["failed_count"]  = failed

    # Save JSON
    out_path = Path("cpr_data.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone! {len(output['stocks'])} stocks saved to cpr_data.json")
    print(f"Failed: {failed}")
    print(f"Generated at: {output['generated_at']}")

if __name__ == "__main__":
    main()
