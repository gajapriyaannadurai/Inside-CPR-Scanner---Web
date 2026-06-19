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
import requests
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
    ("TMPV",        "Tata Motors PV (TMPV)",        "Automobile",           True),
    ("TMCV",        "Tata Motors CV (TMCV)",        "Automobile",           True),
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
    ("MANKIND",     "Mankind Pharma",               "Healthcare",           True),
    ("POLICYBZR",   "PB Fintech (PolicyBazaar)",    "Financial Services",   True),
    ("MAZDOCK",     "Mazagon Dock Shipbuilders",    "Capital Goods",        False),
    ("APARINDS",    "Apar Industries",              "Capital Goods",        False),
    ("KAYNES",      "Kaynes Technology",            "Capital Goods",        False),
    ("TATATECH",    "Tata Technologies",            "Information Technology",False),
    ("NUVAMA",      "Nuvama Wealth Management",     "Financial Services",   False),
    ("SWIGGY",      "Swiggy",                       "Consumer Services",    False),
    ("JSWINFRA",    "JSW Infrastructure",           "Services",             False),
    ("DELHIVERY",   "Delhivery",                    "Services",             False),
    ("AVALON",      "Avalon Technologies",          "Capital Goods",        False),
    ("SENCO",       "Senco Gold",                   "Consumer Durables",    False),
    ("PREMIER",     "Premier Energies",             "Power",                False),
    ("HYUNDAI",     "Hyundai Motor India",          "Automobile",           False),
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
    ("FSL",         "Firstsource Solutions",        "Services",             False),
    ("COCHINSHIP",  "Cochin Shipyard",              "Capital Goods",        False),
    ("AETHER",      "Aether Industries",            "Chemicals",            False),
    ("HSCL",        "Himadri Speciality Chemical",  "Chemicals",            False),
    ("NAVINFLUOR",  "Navin Fluorine",               "Chemicals",            False),
    ("DCMSHRIRAM",  "DCM Shriram",                  "Diversified",          False),
    ("GODREJIND",   "Godrej Industries",            "Diversified",          False),

    # ── Additional Nifty 500 stocks ──
    ("3MINDIA", "3M India", "Diversified", False),
    ("AIAENG", "AIA Engineering", "Capital Goods", False),
    ("ABBOTINDIA", "Abbott India", "Healthcare", False),
    ("ABFRL", "Aditya Birla Fashion", "Consumer Services", True),
    ("ATGL", "Adani Total Gas", "Oil & Gas", False),
    ("AWL", "Adani Wilmar", "FMCG", False),
    ("ADANIENSOL", "Adani Energy Solutions", "Power", False),
    ("AEGISLOG", "Aegis Logistics", "Oil & Gas", False),
    ("AFFLE", "Affle India", "Information Technology", False),
    ("AJANTPHARM", "Ajanta Pharmaceuticals", "Healthcare", False),
    ("ANANDRATHI", "Anand Rathi Wealth", "Financial Services", False),
    ("BEML", "BEML", "Capital Goods", False),
    ("BAJAJHLDNG", "Bajaj Holdings", "Financial Services", True),
    ("MAHABANK", "Bank of Maharashtra", "Financial Services", False),
    ("BATAINDIA", "Bata India", "Consumer Durables", False),
    ("BLUEDART", "Blue Dart Express", "Services", False),
    ("BLUESTARCO", "Blue Star", "Consumer Durables", False),
    ("CEATLTD", "Ceat", "Automobile", True),
    ("EXIDEIND", "Exide Industries", "Automobile", False),
    ("FINCABLES", "Finolex Cables", "Capital Goods", False),
    ("GLENMARK", "Glenmark Pharmaceuticals", "Healthcare", True),
    ("GRANULES", "Granules India", "Healthcare", False),
    ("GUJGASLTD", "Gujarat Gas", "Oil & Gas", False),
    ("MEDANTA", "Global Health (Medanta)", "Healthcare", False),
    ("UBL", "United Breweries", "FMCG", False),
    ("DOMS", "DOMS Industries", "FMCG", False),
    ("CHOLAHLDNG", "Cholamandalam Financial", "Financial Services", False),
    ("JINDALSAW", "Jindal Saw", "Capital Goods", False),
    ("LINDEINDIA", "Linde India", "Chemicals", False),
    ("NUVOCO", "Nuvoco Vistas", "Construction Materials", False),
    ("OIL", "Oil India", "Oil & Gas", False),
    ("ORIENTELEC", "Orient Electric", "Consumer Durables", False),
    ("PGHH", "P&G Hygiene", "FMCG", False),
    ("PRIMEHOTELS", "EIH (Oberoi Hotels)", "Consumer Services", False),
    ("PVRINOX", "PVR INOX", "Consumer Services", False),
    ("SCHAEFFLER", "Schaeffler India", "Automobile", False),
    ("SKFINDIA", "SKF India", "Capital Goods", False),
    ("SUPREMEIND", "Supreme Industries", "Capital Goods", False),
    ("TIINDIA", "Tube Investments", "Automobile", False),
    ("TRIDENT", "Trident", "Textiles", False),
    ("TTKPRESTIG", "TTK Prestige", "Consumer Durables", False),
    ("UCOBANK", "UCO Bank", "Financial Services", False),
    ("UJJIVAN", "Ujjivan Small Finance Bank", "Financial Services", False),
    ("VGUARD", "V-Guard Industries", "Consumer Durables", False),
    ("WHIRLPOOL", "Whirlpool of India", "Consumer Durables", False),
    ("WINDLAS", "Windlas Biotech", "Healthcare", False),
    ("CGCL", "Capri Global Capital", "Financial Services", False),
    ("FINPIPE", "Finolex Industries", "Capital Goods", False),
    ("GAEL", "Gujarat Ambuja Exports", "FMCG", False),
    ("GESHIP", "Great Eastern Shipping", "Services", False),
    ("GPIL", "Godawari Power", "Capital Goods", False),
    ("GSFC", "Gujarat State Fertilizers", "Chemicals", False),
    ("HEG", "HEG", "Capital Goods", False),
    ("HFCL", "HFCL", "Telecom", False),
]

# ─── CPR calculation ──────────────────────────────────────────────────────────
def calc_cpr(h, l, c):
    """
    CPR formula matching GP indicator exactly:
    PP = (High + Low + Close) / 3
    BC = (High + Low) / 2
    TC = PP + (PP - BC)
    """
    pp = (h + l + c) / 3
    bc = (h + l) / 2
    tc = pp + (pp - bc)
    # TC should always be >= BC
    # If inverted (bad data), swap
    if bc > tc:
        tc, bc = bc, tc
    return {"pivot": round(pp, 2), "tc": round(tc, 2), "bc": round(bc, 2)}

def is_inside_cpr(curr, prev):
    """
    Tomorrow's CPR (curr) is inside Today's CPR (prev).
    Chartink checks BOTH normal and inverted CPR cases:

    Case 1 - Normal (TC > BC for both):
        curr.tc < prev.tc AND curr.bc > prev.bc

    Case 2 - Inverted CPR (when BC > TC due to gap/anomaly):
        Both curr TC and BC fall within prev TC and BC range
        i.e. both curr.tc and curr.bc are between prev.bc and prev.tc

    In simple terms: both tomorrow's TC and BC must be
    within today's CPR band (between today's BC and TC).
    """
    prev_high = max(prev["tc"], prev["bc"])
    prev_low  = min(prev["tc"], prev["bc"])
    curr_high = max(curr["tc"], curr["bc"])
    curr_low  = min(curr["tc"], curr["bc"])

    # Tomorrow's entire CPR band must fit inside today's CPR band
    return curr_high < prev_high and curr_low > prev_low



def get_trend(price, cpr):
    """
    Trend based on price position relative to CPR zone:
    - Above TC → Bullish (price trading above top of CPR)
    - Below BC → Bearish (price trading below bottom of CPR)
    - Between TC and BC → Neutral (price inside CPR zone)
    """
    if price > cpr["tc"]:
        return "bullish"
    elif price < cpr["bc"]:
        return "bearish"
    else:
        return "neutral"

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
    "TMPV":        "TMPV.NS",
    "TMCV":        "TMCV.NS",
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
}

# ─── NSE Bhav Copy fetcher ────────────────────────────────────────────────────
# NSE publishes official EOD OHLC for all stocks after 3:30 PM every trading day
# URL format: https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip
# Bhav copy has: SYMBOL, OPEN, HIGH, LOW, CLOSE, VOLUME for all NSE stocks

nse_daily_map = {}  # symbol -> list of last 2 days [{h,l,c,v}]
scan_mode = "DURING_MARKET"  # global, set by fetch_nse_bhav based on IST time

def fetch_nse_bhav():
    """
    Download NSE's official Bhav Copy (EOD file) for the last 2 trading days.
    Populates nse_daily_map with accurate official OHLC data.
    Falls back gracefully if NSE server is unreachable.
    """
    import requests
    import zipfile
    import io
    import csv

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer":    "https://www.nseindia.com",
        "Accept":     "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    global scan_mode
    # ── Time-based date selection (IST) ──────────────────────────────────────
    # Before 3:30 PM IST (market open):
    #   curr = yesterday OHLC  → today's CPR
    #   prev = day-before-yesterday OHLC → yesterday's CPR
    #   Question: Is today's CPR inside yesterday's CPR?
    #
    # After 3:30 PM IST (market closed, today's candle complete):
    #   curr = today OHLC     → tomorrow's CPR
    #   prev = yesterday OHLC → today's CPR
    #   Question: Is tomorrow's CPR inside today's CPR?

    # Get current IST time
    import time as _time
    utc_now   = datetime.datetime.utcnow()
    ist_now   = utc_now + datetime.timedelta(hours=5, minutes=30)
    ist_hhmm  = ist_now.hour * 100 + ist_now.minute  # e.g. 1545 = 3:45 PM
    today     = ist_now.date()
    is_weekday = today.weekday() < 5  # Mon–Fri

    # Market is closed if after 3:30 PM on a weekday
    market_closed = is_weekday and ist_hhmm >= 1530

    if market_closed:
        # After 3:30 PM — use today + yesterday (today candle is complete)
        scan_mode = "AFTER_CLOSE"
        candidate_dates = []
        d = today
        while len(candidate_dates) < 2:
            if d.weekday() < 5:
                candidate_dates.append(d)
            d -= datetime.timedelta(days=1)
        candidate_dates = list(reversed(candidate_dates))
        # [0]=yesterday (prev→today CPR), [1]=today (curr→tomorrow CPR)
    else:
        # Before 3:30 PM — skip today, use yesterday + day-before-yesterday
        scan_mode = "DURING_MARKET"
        candidate_dates = []
        d = today - datetime.timedelta(days=1)  # start from yesterday
        while len(candidate_dates) < 2:
            if d.weekday() < 5:
                candidate_dates.append(d)
            d -= datetime.timedelta(days=1)
        candidate_dates = list(reversed(candidate_dates))
        # [0]=day-before-yesterday (prev→yesterday CPR), [1]=yesterday (curr→today CPR)

    print(f"  IST time: {ist_now.strftime('%H:%M')} | Mode: {scan_mode}")
    if scan_mode == "AFTER_CLOSE":
        print(f"  prev={candidate_dates[0]} (yesterday OHLC → today CPR)")
        print(f"  curr={candidate_dates[1]} (today OHLC → tomorrow CPR)")
        print(f"  Checking: Is tomorrow CPR inside today CPR?")
    else:
        print(f"  prev={candidate_dates[0]} (day-before-yesterday OHLC → yesterday CPR)")
        print(f"  curr={candidate_dates[1]} (yesterday OHLC → today CPR)")
        print(f"  Checking: Is today CPR inside yesterday CPR?")

    session = requests.Session()
    # Warm up session (NSE requires this)
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except:
        pass

    day_data = {}  # date_str -> {symbol: {h,l,c,v}}

    for trade_date in candidate_dates:
        date_str = trade_date.strftime("%Y%m%d")
        # New NSE Bhav Copy URL format
        url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"
        try:
            resp = session.get(url, headers=headers, timeout=30)
            if resp.status_code != 200:
                print(f"  NSE Bhav not available for {trade_date} (HTTP {resp.status_code}) — will use Yahoo")
                continue

            # Unzip and parse CSV
            z = zipfile.ZipFile(io.BytesIO(resp.content))
            csv_name = z.namelist()[0]
            with z.open(csv_name) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                day_data[date_str] = {}
                first_row = True
                for row in reader:
                    # Print column names once for debugging
                    if first_row:
                        print(f"  NSE Bhav columns: {list(row.keys())[:15]}")
                        first_row = False
                    # NSE new Bhav Copy format (confirmed from log):
                    # Columns: TradDt,BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,ISIN,TckrSymb,SctySrs,OpnPric,HghPric,LwPric,ClsPric,LastPric,PrvsClsgPric,UndrlygPric,SttlmPric,OpnIntrst,ChngInOpnIntrst,TtlTradgVol,TtlTrfVal,TtlNbOfTxsExctd,SsnId,NewBrdLotQty,Rmks
                    # NSE old format: SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN
                    sym = row.get("TckrSymb", row.get("SYMBOL", row.get("Symbol", ""))).strip()
                    if not sym: continue
                    # Only process EQ series
                    series = row.get("SctySrs", row.get("SERIES", row.get("Series", "EQ"))).strip()
                    if series not in ("EQ", "BE"):
                        continue
                    try:
                        # New format: HghPric, LwPric, ClsPric, TtlTradgVol
                        # Old format: HIGH, LOW, CLOSE, TOTTRDQTY
                        h = float(row.get("HghPric",     row.get("HIGH",   row.get("high",  0))))
                        l = float(row.get("LwPric",      row.get("LOW",    row.get("low",   0))))
                        c = float(row.get("ClsPric",     row.get("CLOSE",  row.get("close", 0))))
                        v = int(float(row.get("TtlTradgVol", row.get("TOTTRDQTY", row.get("VOLUME", 0)))))
                        if h == 0 or l == 0 or c == 0:
                            continue
                        day_data[date_str][sym] = {"h": h, "l": l, "c": c, "v": v}
                    except (ValueError, KeyError):
                        continue
            print(f"  NSE Bhav {trade_date}: {len(day_data[date_str])} stocks loaded")
        except Exception as e:
            print(f"  NSE Bhav fetch failed for {trade_date}: {e}")

    # Build nse_daily_map: symbol -> [day-before-yesterday, yesterday]
    # sorted ascending = oldest first
    # rows[-2] = day-before-yesterday → yesterday's CPR (prev)
    # rows[-1] = yesterday            → today's CPR    (curr)
    sorted_dates = sorted(day_data.keys())  # ascending: oldest first
    print(f"  Dates sorted ascending: {sorted_dates}")
    print(f"  prev (yesterday CPR) = {sorted_dates[0]} | curr (today CPR) = {sorted_dates[-1]}")
    all_symbols = set()
    for d in sorted_dates:
        all_symbols.update(day_data[d].keys())

    for sym in all_symbols:
        rows = []
        for d in sorted_dates:  # oldest first
            if sym in day_data[d]:
                rows.append(day_data[d][sym])
        if len(rows) >= 2:
            # rows[0] = yesterday (older date) → today's CPR
            # rows[1] = today (newer date)     → tomorrow's CPR
            nse_daily_map[sym] = rows  # [yesterday, today]

    print(f"  NSE map: {len(nse_daily_map)} symbols | prev={sorted_dates[0]} (yesterday CPR) | curr={sorted_dates[-1]} (tomorrow CPR)")
    return len(nse_daily_map) > 0

def get_yahoo_ticker(symbol):
    """Return the correct Yahoo Finance ticker for a given NSE symbol."""
    if symbol in YAHOO_SYMBOL_MAP:
        return YAHOO_SYMBOL_MAP[symbol]
    return symbol + ".NS"

def fetch_stock(symbol):
    """
    Fetch OHLC data.
    Primary  : NSE Bhav Copy (official EOD, accurate, no rate limit)
    Fallback : Yahoo Finance (for weekly/monthly and if NSE fails)
    """
    try:
        yahoo_sym = get_yahoo_ticker(symbol)
        ticker    = yf.Ticker(yahoo_sym)

        # ── Daily: use Yahoo 1d bars (NSE bhav copy pre-loaded into nse_daily_map) ──
        # nse_daily_map is populated by fetch_nse_bhav() before this is called
        # If NSE data available for this symbol use it; otherwise fall back to Yahoo
        d_curr = d_prev = None
        price  = None
        volume = 0
        chg    = 0.0

        if symbol in nse_daily_map and len(nse_daily_map[symbol]) >= 2:
            rows       = nse_daily_map[symbol]
            # rows[0] = day-before-yesterday → yesterday's CPR (prev)
            # rows[1] = yesterday            → today's CPR    (curr)
            # We use only completed candles — today is skipped entirely
            yest_ohlc = rows[-1]   # yesterday's complete OHLC → today's CPR
            dbdy_ohlc = rows[-2]   # day-before-yesterday OHLC → yesterday's CPR

            if yest_ohlc["h"] == 0 or yest_ohlc["l"] == 0 or yest_ohlc["h"] == yest_ohlc["l"]:
                print(f"  WARN {symbol}: bad NSE data h={yest_ohlc['h']} l={yest_ohlc['l']}")
                return None

            # curr = today's CPR    = from yesterday's OHLC
            # prev = yesterday's CPR = from day-before-yesterday's OHLC
            d_curr = yest_ohlc   # → today's CPR
            d_prev = dbdy_ohlc   # → yesterday's CPR
            price  = round(float(yest_ohlc["c"]), 2)
            volume = int(yest_ohlc.get("v", 0))
            chg    = round(((yest_ohlc["c"] - dbdy_ohlc["c"]) / dbdy_ohlc["c"]) * 100, 2) if dbdy_ohlc["c"] else 0

            if symbol in ["HDFCBANK", "RELIANCE", "ALKEM", "ITC"]:
                dc = calc_cpr(yest_ohlc["h"], yest_ohlc["l"], yest_ohlc["c"])
                dp = calc_cpr(dbdy_ohlc["h"], dbdy_ohlc["l"], dbdy_ohlc["c"])
                print(f"  DEBUG {symbol}: yest H={yest_ohlc['h']} L={yest_ohlc['l']} C={yest_ohlc['c']} | dbdy H={dbdy_ohlc['h']} L={dbdy_ohlc['l']} C={dbdy_ohlc['c']}")
                print(f"  DEBUG {symbol}: today_CPR TC={dc['tc']} BC={dc['bc']} | yest_CPR TC={dp['tc']} BC={dp['bc']} | inside={is_inside_cpr(dc,dp)}")
        else:
            # NSE Bhav not available for this symbol — use Yahoo Finance as fallback
            print(f"  INFO {symbol}: not in NSE Bhav, using Yahoo")

        # If daily data not set yet (NSE missing or invalid), use Yahoo
        if d_curr is None or d_prev is None:
            hist = ticker.history(period="15d", interval="1d", auto_adjust=True)
            if hist.empty: return None
            hist = hist.dropna(subset=["High", "Low", "Close"])
            if len(hist) < 2: return None
            d_curr = {"h": float(hist.iloc[-1]["High"]), "l": float(hist.iloc[-1]["Low"]),  "c": float(hist.iloc[-1]["Close"])}
            d_prev = {"h": float(hist.iloc[-2]["High"]), "l": float(hist.iloc[-2]["Low"]),  "c": float(hist.iloc[-2]["Close"])}
            price  = round(float(d_curr["c"]), 2)
            volume = int(hist.iloc[-1]["Volume"]) if "Volume" in hist.columns else 0
            chg    = round(((d_curr["c"] - d_prev["c"]) / d_prev["c"]) * 100, 2) if d_prev["c"] else 0

        if not d_curr or not d_prev: return None

        # ── Weekly OHLC — aggregate from daily bars (Mon-Fri NSE week) ──────────
        # Yahoo 1wk uses Sunday start which doesn't match NSE Mon-Fri week
        # So we build weekly candles from daily data ourselves
        hist_daily = ticker.history(period="6mo", interval="1d", auto_adjust=True).dropna(subset=["High","Low","Close"])
        w_curr = w_prev = None

        if not hist_daily.empty and len(hist_daily) >= 10:
            # Group by ISO week (Mon-Sun) and aggregate OHLC
            import pandas as pd
            df = hist_daily.copy()
            df.index = pd.to_datetime(df.index)
            df['week'] = df.index.to_period('W-FRI')  # Week ending Friday
            weekly = df.groupby('week').agg(
                High=('High','max'),
                Low=('Low','min'),
                Close=('Close','last'),
                Open=('Open','first')
            ).dropna()

            now_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
            current_week = pd.Period(now_ist.date(), 'W-FRI')

            # Determine if the latest aggregated week has fully closed.
            # NSE week closes Friday 3:30 PM IST.
            # current_week.end_time is that week's Friday (23:59:59).
            # If today is BEFORE that Friday, or it IS that Friday but before 3:30 PM,
            # the week is still running and its partial candle must be excluded.
            week_end_date   = current_week.end_time.date()  # the Friday of this period
            is_week_friday  = now_ist.date() == week_end_date
            ist_hhmm        = now_ist.hour * 100 + now_ist.minute
            week_has_closed = (now_ist.date() > week_end_date) or (is_week_friday and ist_hhmm >= 1530)

            # Remove current week from the aggregate ONLY if it hasn't closed yet
            if len(weekly) > 0 and weekly.index[-1] == current_week and not week_has_closed:
                weekly = weekly.iloc[:-1]

            if len(weekly) >= 2:
                w_curr = {"h": float(weekly.iloc[-1]["High"]),  "l": float(weekly.iloc[-1]["Low"]),  "c": float(weekly.iloc[-1]["Close"])}
                w_prev = {"h": float(weekly.iloc[-2]["High"]),  "l": float(weekly.iloc[-2]["Low"]),  "c": float(weekly.iloc[-2]["Close"])}
                if symbol in ["RELIANCE","HDFCBANK","ITC","WIPRO","CIPLA"]:
                    wc = calc_cpr(w_curr["h"], w_curr["l"], w_curr["c"])
                    wp = calc_cpr(w_prev["h"], w_prev["l"], w_prev["c"])
                    print(f"  WK {symbol}: curr_wk={weekly.index[-1]} H={w_curr['h']:.2f} L={w_curr['l']:.2f} C={w_curr['c']:.2f} → TC={wc['tc']} BC={wc['bc']}")
                    print(f"  WK {symbol}: prev_wk={weekly.index[-2]} H={w_prev['h']:.2f} L={w_prev['l']:.2f} C={w_prev['c']:.2f} → TC={wp['tc']} BC={wp['bc']} | inside={is_inside_cpr(wc,wp)}")

        # ── Monthly OHLC — aggregate from daily bars ──────────────────────────────
        hist_daily_long = ticker.history(period="2y", interval="1d", auto_adjust=True).dropna(subset=["High","Low","Close"])
        m_curr = m_prev = None

        if not hist_daily_long.empty and len(hist_daily_long) >= 40:
            import pandas as pd
            df_m = hist_daily_long.copy()
            df_m.index = pd.to_datetime(df_m.index)
            df_m['month'] = df_m.index.to_period('M')
            monthly = df_m.groupby('month').agg(
                High=('High','max'),
                Low=('Low','min'),
                Close=('Close','last'),
                Open=('Open','first')
            ).dropna()

            now_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
            current_month = pd.Period(now_ist.date(), 'M')

            # Determine if the current month has fully closed.
            # Month closes on its last calendar day at 3:30 PM IST (approximation —
            # NSE's actual last trading day can be a day or two earlier on holidays,
            # but daily bar data naturally won't have a bar past the last trading day,
            # so the only real risk is the LAST trading day itself, handled by hhmm check).
            month_end_date  = current_month.end_time.date()  # last calendar day of month
            is_month_end_day = now_ist.date() == month_end_date
            ist_hhmm          = now_ist.hour * 100 + now_ist.minute
            month_has_closed = (now_ist.date() > month_end_date) or (is_month_end_day and ist_hhmm >= 1530)

            # Remove current month from aggregate ONLY if it hasn't closed yet
            if len(monthly) > 0 and monthly.index[-1] == current_month and not month_has_closed:
                monthly = monthly.iloc[:-1]

            if len(monthly) >= 2:
                m_curr = {"h": float(monthly.iloc[-1]["High"]), "l": float(monthly.iloc[-1]["Low"]), "c": float(monthly.iloc[-1]["Close"])}
                m_prev = {"h": float(monthly.iloc[-2]["High"]), "l": float(monthly.iloc[-2]["Low"]), "c": float(monthly.iloc[-2]["Close"])}

        # ── CPR trend: last 5 daily pivots from Yahoo ──
        hist_5d = ticker.history(period="15d", interval="1d", auto_adjust=True).dropna(subset=["High","Low","Close"]).tail(5)
        pivots  = [round((row["High"]+row["Low"]+row["Close"])/3, 2) for _, row in hist_5d.iterrows()]

        return {
            "symbol":  symbol,
            "price":   price,
            "change":  chg,
            "volume":  volume,
            "source":  "NSE" if (symbol in nse_daily_map and d_curr and d_curr["h"] != d_curr["l"] and d_curr["h"] != 0) else "Yahoo",
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

    # ── Step 1: Fetch NSE Bhav Copy (official EOD data) ──────────────────────
    print("\n[Step 1] Fetching NSE Bhav Copy (official EOD OHLC)...")
    nse_ok = fetch_nse_bhav()
    if nse_ok:
        print(f"  NSE Bhav loaded — {len(nse_daily_map)} symbols available")
    else:
        print("  NSE Bhav unavailable — will use Yahoo Finance for all stocks")

    # ── Step 2: Process each stock ────────────────────────────────────────────
    print(f"\n[Step 2] Processing {len(STOCKS)} stocks...")

    output = {
        "generated_at":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST"),
        "generated_date": datetime.datetime.now().strftime("%d %b %Y"),
        "scan_mode":      scan_mode,   # AFTER_CLOSE or DURING_MARKET
        "scan_logic":     "AFTER_CLOSE: tomorrow CPR (today OHLC) inside today CPR (yesterday OHLC) | DURING_MARKET: today CPR (yesterday OHLC) inside yesterday CPR (day-before-yesterday OHLC)",
        "total_stocks":   len(STOCKS),
        "stocks":         []
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

    # ── Debug summary — shows CPR values for first 5 stocks ──
    debug = []
    for s in output["stocks"][:5]:
        d = s.get("daily", {})
        debug.append({
            "symbol":   s["symbol"],
            "price":    s["price"],
            "source":   s.get("source","?"),
            "curr_tc":  d.get("curr_cpr",{}).get("tc"),
            "curr_bc":  d.get("curr_cpr",{}).get("bc"),
            "prev_tc":  d.get("prev_cpr",{}).get("tc"),
            "prev_bc":  d.get("prev_cpr",{}).get("bc"),
            "inside":   d.get("inside"),
            "curr_tc_lt_prev_tc": (d.get("curr_cpr",{}).get("tc",0) < d.get("prev_cpr",{}).get("tc",1)),
            "curr_bc_gt_prev_bc": (d.get("curr_cpr",{}).get("bc",1) > d.get("prev_cpr",{}).get("bc",0)),
        })
    output["debug_first5"] = debug
    output["inside_count"] = sum(1 for s in output["stocks"] if s.get("daily",{}).get("inside"))

    # Save JSON
    out_path = Path("cpr_data.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone! {len(output['stocks'])} stocks saved to cpr_data.json")
    print(f"Inside CPR (daily): {output['inside_count']} stocks")
    print(f"Failed: {failed}")
    print(f"Generated at: {output['generated_at']}")
    print(f"\nDebug — first 5 stocks CPR values:")
    for d in output["debug_first5"]:
        print(f"  {d['symbol']}: price={d['price']} source={d['source']} curr_tc={d['curr_tc']} curr_bc={d['curr_bc']} prev_tc={d['prev_tc']} prev_bc={d['prev_bc']} inside={d['inside']} (tc<prevtc:{d['curr_tc_lt_prev_tc']} bc>prevbc:{d['curr_bc_gt_prev_bc']})")

if __name__ == "__main__":
    main()
