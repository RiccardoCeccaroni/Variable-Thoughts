"""
Score all extracted predictions against the actuals reference table.
For predictions that don't match the reference table, flags them for manual/API lookup.
"""

import json
import os
import re
import math

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
JSON_DIR = os.path.join(BASE_DIR, "extracted", "raw_json")
REF_FILE = os.path.join(BASE_DIR, "data", "benchmarks", "actuals_reference.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "results")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_reference():
    with open(REF_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_all_predictions():
    preds = []
    for fname in sorted(os.listdir(JSON_DIR)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(JSON_DIR, fname), encoding="utf-8") as f:
            data = json.load(f)
        company = data.get("company", "")
        pub_date = data.get("publication_date", "")
        report_year = data.get("report_year", "")
        for i, pred in enumerate(data.get("predictions", [])):
            if pred.get("not_scoreable"):
                continue
            preds.append({
                "pred_id": f"{fname}_{i}",
                "file": fname,
                "company": company,
                "publication_date": pub_date,
                "report_year": report_year,
                **pred,
            })
    return preds


def parse_number(val_str):
    """Extract a numeric value from a string like '4%', '~5%', '2.3%-2.6%', '$1,500/barrel'."""
    if not val_str or not isinstance(val_str, str):
        return None
    s = val_str.strip()
    # Remove commas from numbers (e.g., "1,500" -> "1500")
    s = re.sub(r'(\d),(\d)', r'\1\2', s)

    # Handle ranges: take midpoint
    range_match = re.search(r'(-?[\d.]+)\s*[%]?\s*[-–—to]+\s*(-?[\d.]+)\s*%?', s)
    if range_match:
        lo = float(range_match.group(1))
        hi = float(range_match.group(2))
        return (lo + hi) / 2.0

    # Single number
    num_match = re.search(r'[~≈≥≤><$€£¥]?\s*(-?[\d.]+)', s)
    if num_match:
        return float(num_match.group(1))
    return None


def extract_year(horizon):
    """Extract the target year from a horizon string."""
    if not horizon:
        return None
    # "2023 calendar year", "2023", "year-end 2022", "Q3 2022 to Q3 2023"
    # For ranges, take the end year
    years = re.findall(r'20[12]\d', horizon)
    if years:
        return years[-1]  # last mentioned year
    return None


def is_midyear_horizon(horizon):
    """Check if horizon refers to mid-year / H1 / June / Q2."""
    if not horizon:
        return False
    h = horizon.lower()
    return any(k in h for k in ['mid-', 'midyear', 'mid year', 'june', 'h1', 'q2',
                                  'first half', '6 months', 'spring'])


def is_yearend_horizon(horizon):
    """Check if horizon refers to year-end / December / Q4."""
    if not horizon:
        return False
    h = horizon.lower()
    return any(k in h for k in ['year-end', 'yearend', 'year end', 'december', 'dec ',
                                  'q4', 'end of', 'end-of', 'h2', 'second half'])


def normalize_region(region):
    """Normalize region names for matching."""
    r = region.strip().lower()
    mappings = {
        'us': 'US', 'u.s.': 'US', 'united states': 'US', 'america': 'US', 'usa': 'US',
        'euro area': 'Eurozone', 'eurozone': 'Eurozone', 'euro zone': 'Eurozone',
        'ea': 'Eurozone', 'emu': 'Eurozone',
        'uk': 'UK', 'u.k.': 'UK', 'united kingdom': 'UK', 'britain': 'UK',
        'china': 'China', 'japan': 'Japan', 'india': 'India', 'brazil': 'Brazil',
        'germany': 'Germany', 'france': 'France', 'italy': 'Italy', 'spain': 'Spain',
        'switzerland': 'Switzerland', 'russia': 'Russia',
        'europe': 'Eurozone',
        'global': 'Global', 'world': 'Global',
        'dm': 'DM', 'developed markets': 'DM', 'developed': 'DM',
        'em': 'EM', 'emerging markets': 'EM', 'emerging': 'EM',
        'mexico': 'Mexico', 'brim': 'BRIM',
    }
    return mappings.get(r, region)


def match_gdp(pred, ref, year):
    region = normalize_region(pred["region"])
    variable = pred.get("variable", "").lower()
    gdp = ref.get("gdp_growth_annual", {})

    # Handle "relative" growth predictions - still use the target year's GDP
    if "relative" in variable and year:
        pass  # fall through to standard lookup

    # Handle "recession" variable names
    if "recession" in variable and region in gdp and year in gdp[region]:
        return gdp[region][year], gdp[region].get("source", ""), "gdp_growth_annual"

    if region in gdp and year in gdp[region]:
        return gdp[region][year], gdp[region].get("source", ""), "gdp_growth_annual"
    return None, None, None


def match_cpi(pred, ref, year):
    region = normalize_region(pred["region"])
    variable = pred["variable"].lower()
    horizon = pred.get("horizon", "").lower()

    # Core PCE
    if "core pce" in variable or "pce" in variable:
        pce = ref.get("core_pce_yoy", {})
        if is_yearend_horizon(pred.get("horizon", "")) or "december" in horizon:
            key = "US_december"
        else:
            key = "US_annual_avg"
        if key in pce and year in pce[key]:
            return pce[key][year], pce[key].get("source", "BEA PCE"), "core_pce_yoy"

    # CPI December YoY
    if is_yearend_horizon(pred.get("horizon", "")):
        dec = ref.get("cpi_december_yoy", {})
        if region in dec and year in dec[region]:
            return dec[region][year], dec[region].get("source", ""), "cpi_december_yoy"

    # CPI annual average (default)
    cpi = ref.get("cpi_annual_average", {})
    if region in cpi and year in cpi[region]:
        return cpi[region][year], cpi[region].get("source", ""), "cpi_annual_average"

    return None, None, None


def match_unemployment(pred, ref, year):
    region = normalize_region(pred["region"])
    horizon = pred.get("horizon", "").lower()
    unemp = ref.get("unemployment_rate", {})

    if region == "US":
        if "mid" in horizon or "june" in horizon or "q2" in horizon:
            key = "US_midyear"
        elif "q4" in horizon or "year-end" in horizon or "yearend" in horizon or "december" in horizon:
            key = "US_Q4"
        elif "annual" in horizon or "average" in horizon:
            key = "US_annual"
        else:
            key = "US_yearend"
        if key in unemp and year in unemp[key]:
            return unemp[key][year], unemp[key].get("source", "BLS"), "unemployment_rate"
    elif region == "UK":
        key = "UK_yearend"
        if key in unemp and year in unemp[key]:
            return unemp[key][year], unemp[key].get("source", "ONS"), "unemployment_rate"
    elif region == "Eurozone":
        key = "Eurozone_yearend"
        if key in unemp and year in unemp[key]:
            return unemp[key][year], unemp[key].get("source", "Eurostat"), "unemployment_rate"
    return None, None, None


def match_policy_rate(pred, ref, year):
    region = normalize_region(pred["region"])
    variable = pred["variable"].lower()
    horizon = pred.get("horizon", "").lower()

    eop = ref.get("policy_rates_end_of_period", {})
    mid = ref.get("policy_rates_midyear", {})

    use_mid = is_midyear_horizon(pred.get("horizon", ""))

    if region == "US" or "fed" in variable or "federal" in variable:
        if use_mid:
            key = "fed_funds_upper_june"
            if key in mid and year in mid[key]:
                return mid[key][year], mid[key].get("source", "Federal Reserve"), "policy_rates_midyear"
        key = "fed_funds_upper"
        if key in eop and year in eop[key]:
            return eop[key][year], eop[key].get("source", "Federal Reserve"), "policy_rates_end_of_period"

    elif region == "Eurozone" or "ecb" in variable:
        if "deposit" in variable or "ecb" in variable:
            if use_mid:
                key = "ecb_deposit_june"
                if key in mid and year in mid[key]:
                    return mid[key][year], mid[key].get("source", "ECB"), "policy_rates_midyear"
            key = "ecb_deposit"
            if key in eop and year in eop[key]:
                return eop[key][year], eop[key].get("source", "ECB"), "policy_rates_end_of_period"
        if "refi" in variable or "main" in variable:
            key = "ecb_main_refi"
            if key in eop and year in eop[key]:
                return eop[key][year], eop[key].get("source", "ECB"), "policy_rates_end_of_period"

    elif region == "UK" or "boe" in variable or "bank of england" in variable:
        if use_mid:
            key = "boe_bank_rate_june"
            if key in mid and year in mid[key]:
                return mid[key][year], mid[key].get("source", "Bank of England"), "policy_rates_midyear"
        key = "boe_bank_rate"
        if key in eop and year in eop[key]:
            return eop[key][year], eop[key].get("source", "Bank of England"), "policy_rates_end_of_period"

    elif region == "Japan" or "boj" in variable or "bank of japan" in variable:
        key = "boj_policy_rate"
        if key in eop and year in eop[key]:
            return eop[key][year], eop[key].get("source", "Bank of Japan"), "policy_rates_end_of_period"

    return None, None, None


def match_treasury(pred, ref, year):
    variable = pred["variable"].lower()
    horizon = pred.get("horizon", "")
    yields = ref.get("treasury_yields_end_of_period", {})

    use_mid = is_midyear_horizon(horizon)

    if "10" in variable or "ten" in variable:
        if "german" in variable or "bund" in variable:
            key = "german_10y_june" if use_mid else "german_10y"
        elif "japan" in variable:
            key = "japan_10y"
        else:
            key = "us_10y_june" if use_mid else "us_10y"
        if key in yields and year in yields[key]:
            return yields[key][year], yields[key].get("source", ""), "treasury_yields"

    if "2-year" in variable or "2y" in variable or "two-year" in variable:
        key = "us_2y"
        if key in yields and year in yields[key]:
            return yields[key][year], yields[key].get("source", ""), "treasury_yields"

    return None, None, None


def match_equity(pred, ref, year):
    variable = pred["variable"].lower()
    region = normalize_region(pred["region"])
    horizon = pred.get("horizon", "")
    eq = ref.get("equity_indices_end_of_period", {})

    use_mid = is_midyear_horizon(horizon)

    if "corporate profit" in variable or "s&p" in variable or "sp500" in variable or "s&p 500" in variable:
        if "eps" in variable or "earnings" in variable or "profit" in variable:
            eps = ref.get("sp500_eps", {})
            if "growth" in variable:
                key = "yoy_growth_pct"
            else:
                key = "operating_eps"
            if key in eps and year in eps[key]:
                return eps[key][year], eps[key].get("source", "S&P / FactSet"), "sp500_eps"
        # Index level / return
        key = "sp500_june" if use_mid else "sp500"
        if key in eq and year in eq[key]:
            return eq[key][year], eq[key].get("source", "Bloomberg"), "equity_indices"

    if "euro stoxx" in variable or "eurostoxx" in variable:
        key = "euro_stoxx_50"
        if key in eq and year in eq[key]:
            return eq[key][year], eq[key].get("source", "Bloomberg"), "equity_indices"

    if "topix" in variable:
        key = "topix"
        if key in eq and year in eq[key]:
            return eq[key][year], eq[key].get("source", "JPX"), "equity_indices"

    if "msci em" in variable or ("msci" in variable and ("emerging" in variable or region == "EM")):
        key = "msci_em"
        if key in eq and year in eq[key]:
            return eq[key][year], eq[key].get("source", "MSCI"), "equity_indices"

    if "msci europe" in variable or ("msci" in variable and region in ("Europe", "Eurozone")):
        key = "msci_europe"
        if key in eq and year in eq[key]:
            return eq[key][year], eq[key].get("source", "MSCI"), "equity_indices"

    # MSCI US -> approximate with S&P 500 (highly correlated)
    if "msci" in variable and ("us" in variable.split() or region == "US"):
        key = "sp500_june" if is_midyear_horizon(horizon) else "sp500"
        if key in eq and year in eq[key]:
            return eq[key][year], eq[key].get("source", "Bloomberg (S&P 500 proxy)"), "equity_indices"

    return None, None, None


def match_fx(pred, ref, year):
    variable = pred["variable"].lower()
    horizon = pred.get("horizon", "")
    fx = ref.get("fx_end_of_period", {})

    key = None
    if "eur" in variable and "usd" in variable:
        key = "eurusd"
    elif "usd" in variable and "jpy" in variable:
        key = "usdjpy"
    elif "usd" in variable and "cny" in variable:
        key = "usdcny"
    elif "aud" in variable and "usd" in variable:
        key = "audusd"
    elif "dxy" in variable or "dollar index" in variable or "trade-weighted" in variable:
        dxy = ref.get("dxy_end_of_period", {})
        if year in dxy:
            return dxy[year], dxy.get("source", "ICE DXY"), "dxy"
        return None, None, None

    if key is None:
        return None, None, None

    # Check midyear FX data
    if is_midyear_horizon(horizon):
        mid_key = f"{key}_june"
        fx_mid = ref.get("fx_midyear", {})
        if mid_key in fx_mid and year in fx_mid[mid_key]:
            return fx_mid[mid_key][year], fx_mid[mid_key].get("source", "Bloomberg"), "fx_midyear"

    if key in fx and year in fx[key]:
        return fx[key][year], fx[key].get("source", "Bloomberg"), "fx"
    return None, None, None


def match_commodity(pred, ref, year):
    variable = pred["variable"].lower()
    horizon = pred.get("horizon", "").lower()
    comm = ref.get("commodities_end_of_period", {})

    if "brent" in variable:
        if "average" in horizon or "avg" in horizon:
            key = "brent_crude_annual_avg"
        else:
            key = "brent_crude"
        if key in comm and year in comm[key]:
            return comm[key][year], comm[key].get("source", "ICE"), "commodities"

    if "wti" in variable:
        if is_midyear_horizon(horizon):
            key = "wti_crude_june"
        else:
            key = "wti_crude"
        if key in comm and year in comm[key]:
            return comm[key][year], comm[key].get("source", "NYMEX"), "commodities"

    if "gold" in variable:
        if is_midyear_horizon(horizon):
            key = "gold_june"
        else:
            key = "gold"
        if key in comm and year in comm[key]:
            return comm[key][year], comm[key].get("source", "LBMA"), "commodities"

    # Generic oil
    if "oil" in variable or "crude" in variable:
        if "average" in horizon or "avg" in horizon:
            key = "brent_crude_annual_avg"
        else:
            key = "brent_crude"
        if key in comm and year in comm[key]:
            return comm[key][year], comm[key].get("source", "ICE"), "commodities"

    return None, None, None


def match_credit(pred, ref, year):
    variable = pred["variable"].lower()
    horizon = pred.get("horizon", "")
    credit = ref.get("credit_spreads_end_of_period", {})
    credit_mid = ref.get("credit_spreads_midyear", {})

    if "ig" in variable or "investment grade" in variable or "investment-grade" in variable:
        if is_midyear_horizon(horizon):
            key = "us_ig_oas_june"
            if key in credit_mid and year in credit_mid[key]:
                return credit_mid[key][year], credit_mid[key].get("source", "Bloomberg"), "credit_spreads_midyear"
        key = "us_ig_oas"
    elif "hy" in variable or "high yield" in variable:
        key = "us_hy_oas"
    elif "embi" in variable or "em bond" in variable or "embig" in variable:
        key = "embig_spread"
    else:
        return None, None, None

    if key in credit and year in credit[key]:
        return credit[key][year], credit[key].get("source", "Bloomberg"), "credit_spreads"
    return None, None, None


def classify_variable(pred):
    """Determine which matching function to use. Order matters: more specific checks first."""
    cat = pred.get("category", "").lower()
    var = pred.get("variable", "").lower()

    # Most specific checks first - commodity keywords
    if "gold" in var or "oil" in var or "brent" in var or "wti" in var or "crude" in var or "gas" in var:
        return "commodity"
    if cat == "commodities":
        return "commodity"

    # Credit spreads before fx (both might have "usd")
    if "spread" in var or "oas" in var or "credit" in var:
        return "credit"

    # GDP / growth
    if "gdp" in var:
        return "gdp"
    if cat == "growth":
        if "eps" in var or "earnings" in var:
            return "equity"
        if "recession" in var:
            return "gdp"
        return "gdp"

    # Inflation
    if "cpi" in var or "pce" in var:
        return "cpi"
    if cat == "inflation":
        if "wage" in var:
            return "other"
        return "cpi"

    # Labor
    if cat == "labor" or "unemployment" in var or "jobless" in var:
        return "unemployment"

    # Equities (before fx/policy_rate since equity vars might contain "usd" or "rate")
    if cat == "equities" or "s&p" in var or "stoxx" in var or "topix" in var or "msci" in var:
        return "equity"
    if "eps" in var or "earnings" in var:
        return "equity"

    # Treasury / fixed income yields
    if "treasury" in var or "10-year" in var or "10y" in var or "2-year" in var or "2y" in var:
        return "treasury"
    if "yield" in var and "bond" in var:
        return "treasury"
    if cat == "fixed_income":
        if "yield" in var or "treasury" in var:
            return "treasury"
        if "spread" in var:
            return "credit"
        return "treasury"

    # FX - check for specific currency pairs
    if "eur/usd" in var or "eurusd" in var or "usd/jpy" in var or "usdjpy" in var:
        return "fx"
    if "usd/cny" in var or "aud/usd" in var or "dxy" in var or "dollar index" in var:
        return "fx"
    if cat == "fx":
        return "fx"

    # Monetary policy - last among the rate-containing checks
    if cat == "monetary_policy":
        return "policy_rate"
    if ("fed fund" in var or "federal" in var or "ecb" in var or "boe" in var or
            "boj" in var or "bank of england" in var or "bank of japan" in var):
        return "policy_rate"

    return "other"


def try_match(pred, ref):
    """Try to match a prediction against the reference table. Returns (actual, source, ref_key) or (None, None, None)."""
    year = extract_year(pred.get("horizon", ""))
    if not year:
        return None, None, None

    vtype = classify_variable(pred)

    matchers = {
        "gdp": match_gdp,
        "cpi": match_cpi,
        "unemployment": match_unemployment,
        "policy_rate": match_policy_rate,
        "treasury": match_treasury,
        "equity": match_equity,
        "fx": match_fx,
        "commodity": match_commodity,
        "credit": match_credit,
    }

    if vtype in matchers:
        return matchers[vtype](pred, ref, year)

    return None, None, None


def is_qualitative(forecast_value):
    """Check if a forecast value is qualitative rather than numeric."""
    if not forecast_value:
        return True
    v = forecast_value.lower().strip()
    qualitative_keywords = [
        "recession", "no recession", "slowing", "decline", "rising", "falling",
        "above", "below", "higher", "lower", "positive", "negative",
        "overweight", "underweight", "outperform", "underperform",
        "hawkish", "dovish", "tightening", "easing", "pause",
        "single-digit", "double-digit", "moderate", "modest",
        "depreciation", "appreciation", "narrowing", "widening",
        "no rate hike", "no change", "unchanged",
    ]
    # If it's purely qualitative
    if any(kw in v for kw in qualitative_keywords) and not re.search(r'\d+\.?\d*\s*%', v):
        return True
    return False


def score_qualitative(pred, actual_value, forecast_value):
    """Score qualitative predictions where possible."""
    fv = forecast_value.lower()
    variable = pred.get("variable", "").lower()

    # Handle "recession" / "contraction" predictions
    if "recession" in fv or "contraction" in fv:
        if actual_value is not None and isinstance(actual_value, (int, float)):
            if "no recession" in fv or "unlikely" in fv:
                if actual_value < 0:
                    return "incorrect", "Predicted no recession, but GDP contracted"
                else:
                    return "correct", "Correctly predicted no recession"
            else:
                if actual_value < 0:
                    return "correct", "Correctly predicted recession/contraction"
                else:
                    return "incorrect", "Predicted recession but GDP was positive"

    # "mild downturn" / "downturn" predictions
    if "downturn" in fv or "slowdown" in fv:
        if actual_value is not None and isinstance(actual_value, (int, float)):
            if actual_value > 0:
                return "incorrect", f"Predicted downturn but growth was {actual_value}%"
            else:
                return "correct", f"Correctly predicted downturn (actual: {actual_value}%)"

    # "on hold" / "unchanged" rate predictions
    if "on hold" in fv or "unchanged" in fv or "no change" in fv:
        return "qualitative", "Rate direction prediction - manual review needed"

    # "peaked" / "peak" predictions
    if "peak" in fv:
        return "qualitative", "Peak timing prediction - manual review needed"

    # "pickup" / "growth" / "recovery"
    if any(w in fv for w in ["pickup", "recovery", "restart", "rebound"]):
        if actual_value is not None and isinstance(actual_value, (int, float)):
            if actual_value > 0:
                return "correct", f"Correctly predicted positive growth (actual: {actual_value}%)"
            else:
                return "incorrect", f"Predicted growth but actual was {actual_value}%"

    # "bear market" / "decline"
    if "bear market" in fv:
        if actual_value is not None and isinstance(actual_value, (int, float)):
            # For equity predictions, a bear market means >20% decline
            return "qualitative", "Bear market prediction"

    # Directional calls
    if any(w in fv for w in ["rising", "higher", "increase", "above", "upside"]):
        return "directional", None
    if any(w in fv for w in ["falling", "lower", "decline", "below", "dampen", "slow", "deflation", "fall"]):
        return "directional_down", None

    return "qualitative", None


def compute_error(forecast_val, actual_val):
    """Compute error metrics."""
    if forecast_val is None or actual_val is None:
        return None, None, None

    error = actual_val - forecast_val  # positive = actual higher than forecast
    magnitude = abs(error)

    # Percentage error (relative to actual, avoiding div by zero)
    if actual_val != 0:
        pct = (error / abs(actual_val)) * 100
    elif forecast_val != 0:
        pct = (error / abs(forecast_val)) * 100
    else:
        pct = 0

    return error, magnitude, pct


def determine_direction(error):
    """Determine if forecast was too high, too low, or correct."""
    if error is None:
        return "not_determined"
    if abs(error) < 0.05:  # within 0.05 pp
        return "correct"
    elif error > 0:
        return "too_low"  # actual > forecast means forecast was too low
    else:
        return "too_high"  # actual < forecast means forecast was too high


def build_description(pred):
    """Build a brief descriptive phrase for the prediction."""
    var = pred["variable"]
    region = pred["region"]
    horizon = pred.get("horizon", "")
    return f"{var} ({region}, {horizon})"


def guess_unit(pred, ref_key):
    """Determine the unit label for the error magnitude."""
    variable = pred.get("variable", "").lower()
    cat = pred.get("category", "").lower()

    if any(k in variable for k in ["gold", "oil", "crude", "brent", "wti", "gas price"]):
        return "units"
    if any(k in variable for k in ["s&p", "stoxx", "topix", "msci", "smi", "index level"]):
        return "points"
    if cat == "commodities":
        return "units"
    if "spread" in variable or "oas" in variable:
        return "bps"
    if "eur/usd" in variable or "usd/jpy" in variable or "usd/cny" in variable or "aud/usd" in variable:
        return "units"
    if "dxy" in variable:
        return "points"
    if ref_key in ("equity_indices", "commodities", "fx", "fx_midyear", "dxy"):
        return "units"
    if ref_key in ("credit_spreads", "credit_spreads_midyear"):
        return "bps"
    return "pp"


def format_error_unit(unit):
    if unit == "pp":
        return "percentage points"
    if unit == "bps":
        return "basis points"
    if unit == "points":
        return "points"
    return ""  # no unit suffix for dollars/generic


def build_result_summary(pred, actual_val, actual_source, error_dir, error_mag, forecast_num, ref_key=""):
    """Build the human-readable result summary sentence."""
    company = pred["company"]
    variable = pred["variable"]
    region = pred["region"]
    horizon = pred.get("horizon", "")
    forecast = pred["forecast_value"]

    if actual_val is None:
        return f"{company} predicted {variable} for {region} at {horizon} would be {forecast}. Actual value could not be matched from reference table."

    # Format actual value
    actual_str = str(actual_val)
    if isinstance(actual_val, float) and actual_val == int(actual_val) and abs(actual_val) < 10000:
        actual_str = f"{actual_val:.1f}"

    source_str = f" ({actual_source})" if actual_source else ""
    unit = guess_unit(pred, ref_key)
    unit_label = format_error_unit(unit)

    if error_dir == "correct":
        return f"{company} predicted {variable} for {region} at {horizon} would be {forecast}. Actual was {actual_str}{source_str}. The forecast was essentially correct."

    if error_mag is not None:
        mag_str = f"{error_mag:.1f}"
        suffix = f" {unit_label}" if unit_label else ""
        if error_dir == "too_high":
            return f"{company} predicted {variable} for {region} at {horizon} would be {forecast}. Actual was {actual_str}{source_str}. The forecast was too high by {mag_str}{suffix}."
        elif error_dir == "too_low":
            return f"{company} predicted {variable} for {region} at {horizon} would be {forecast}. Actual was {actual_str}{source_str}. The forecast was too low by {mag_str}{suffix}."

    return f"{company} predicted {variable} for {region} at {horizon} would be {forecast}. Actual was {actual_str}{source_str}."


def determine_unit(ref_key, variable):
    """Determine the unit of measurement for proper formatting."""
    if ref_key in ("gdp_growth_annual", "cpi_annual_average", "cpi_december_yoy",
                    "core_pce_yoy", "unemployment_rate", "sp500_eps"):
        return "pct_points"
    if ref_key in ("policy_rates_end_of_period", "policy_rates_midyear", "treasury_yields"):
        return "pct_points"
    if ref_key in ("equity_indices",):
        return "points"
    if ref_key in ("fx",):
        return "units"
    if ref_key in ("commodities",):
        return "dollars"
    if ref_key in ("credit_spreads",):
        return "bps"
    return "pct_points"


def handle_timing_predictions(pred, ref):
    """Handle predictions about timing of events (rate hikes, etc.)."""
    variable = pred["variable"].lower()
    forecast = pred["forecast_value"].lower()
    events = ref.get("key_events", {})

    # Fed first hike timing
    if ("fed" in variable and "hike" in variable) or ("fed" in variable and "first" in variable and "rate" in variable):
        actual_date = events.get("fed_first_hike_2022", "")
        if actual_date:
            return {
                "actual_value": actual_date,
                "actual_source": "Federal Reserve",
                "ref_key": "key_events",
                "is_timing": True,
            }

    # ECB first hike timing
    if ("ecb" in variable and "hike" in variable) or ("ecb" in variable and "first" in variable):
        actual_date = events.get("ecb_first_hike_2022", "")
        if actual_date:
            return {
                "actual_value": actual_date,
                "actual_source": "ECB",
                "ref_key": "key_events",
                "is_timing": True,
            }

    # BoE first hike
    if ("boe" in variable or "bank of england" in variable) and ("hike" in variable or "first" in variable):
        actual_date = events.get("boe_first_hike_2021", "")
        if actual_date:
            return {
                "actual_value": actual_date,
                "actual_source": "Bank of England",
                "ref_key": "key_events",
                "is_timing": True,
            }

    # Fed first cut
    if ("fed" in variable and "cut" in variable):
        actual_date = events.get("fed_first_cut_2024", "")
        if actual_date:
            return {
                "actual_value": actual_date,
                "actual_source": "Federal Reserve",
                "ref_key": "key_events",
                "is_timing": True,
            }

    return None


MANUAL_ACTUALS = {
    # Brazil Selic rate
    "amundi_2023.json_26": {
        "actual_value": 12.25, "actual_source": "BCB (Banco Central do Brasil)",
        "note": "Selic was 12.25% at end-Nov 2023 (cut from 13.75% starting Aug 2023)"
    },
    "amundi_2024.json_27": {
        "actual_value": 12.25, "actual_source": "BCB (Banco Central do Brasil)",
        "note": "Selic was raised to 12.25% in Dec 2024"
    },
    # China MLF rate
    "vanguard_2023.json_14": {
        "actual_value": 2.5, "actual_source": "PBoC",
        "note": "1-year MLF rate was 2.5% at end-2023 (cut from 2.75% to 2.5% in Aug 2023)"
    },
    "vanguard_2024.json_16": {
        "actual_value": 2.0, "actual_source": "PBoC",
        "note": "1-year MLF rate was 2.0% at end-2024 (cut to 2.3% Jul, then 2.0% Sep 2024)"
    },
    # PBoC rate cut H2 2024
    "amundi_2024.json_44": {
        "actual_value": "50bp of cuts (20bp Jul + 30bp Sep)",
        "actual_source": "PBoC",
        "note": "PBoC cut MLF rate by 20bp in Jul 2024 and 30bp in Sep 2024, totaling 50bp in H2",
        "assessment": "correct", "qualitative": True
    },
    # European natural gas TTF 2023 average
    "amundi_2023.json_24": {
        "actual_value": 41, "actual_source": "ICE Endex TTF",
        "note": "TTF averaged ~EUR 41/MWh in 2023, far below forecast of EUR 100-150/MWh"
    },
    # SMI June 2021
    "ubs_2021.json_3": {
        "actual_value": 12045, "actual_source": "SIX Swiss Exchange",
        "note": "SMI reached ~12,045 at end June 2021 (crossed 12,000 milestone on Jun 17)"
    },
    # SNB final rate hike timing
    "ubs_2023.json_6": {
        "actual_value": "June 2023 (25bp hike)",
        "actual_source": "SNB",
        "note": "SNB's last hike was Jun 2023, later than Q1/Q2 forecast. Held in Sep 2023.",
        "assessment": "partially_correct", "qualitative": True
    },
    # Fed terminal rate (Vanguard 2022 predicted "at least 2.5%")
    "vanguard_2022.json_10": {
        "actual_value": 5.50, "actual_source": "Federal Reserve",
        "note": "Fed funds peaked at 5.25-5.50% in Jul 2023. Forecast of 'at least 2.5%' was correct in direction but magnitude was far off."
    },
    # MSCI World EPS growth 2022
    "amundi_2022.json_23": {
        "actual_value": 7.3, "actual_source": "MSCI / FactSet",
        "note": "MSCI World forward EPS growth in 2022 was approx 7-8% (close to +8% forecast)"
    },
    # MSCI World AC index level Q4 2024
    "amundi_2024.json_39": {
        "actual_value": 838, "actual_source": "MSCI",
        "note": "MSCI ACWI ended 2024 at approximately 838 (17.5% return in 2024)"
    },
    # MSCI US index level (proxy with S&P 500 won't work since Amundi used MSCI US scale)
    # Amundi 2024 MSCI US Q4 2024: MSCI USA index ended 2024 at ~5270
    "amundi_2024.json_37": {
        "actual_value": 5270, "actual_source": "MSCI USA Index (approx)",
        "note": "MSCI USA index ended Q4 2024 at approx 5270"
    },
    # Global inflation 2020 (UBS)
    "ubs_2020.json_15": {
        "actual_value": 1.9, "actual_source": "IMF WEO",
        "note": "Global consumer price inflation averaged ~1.9% in 2020 (IMF)"
    },
    # Sydney/Melbourne property 2019
    "fidelity_2019.json_1": {
        "actual_value": "Rose ~5% (Sydney) / ~3% (Melbourne) in H2 2019",
        "actual_source": "CoreLogic Australia",
        "note": "After declining in H1, prices rebounded sharply from mid-2019. Forecast of 'flat to slightly down' was wrong.",
        "assessment": "incorrect", "qualitative": True
    },
    # BoE rate hike expectations (BlackRock 2023: "unrealistically hawkish")
    "blackrock_2023.json_4": {
        "actual_value": "BoE raised from 3.0% to 5.25% by Aug 2023",
        "actual_source": "Bank of England",
        "note": "Markets were pricing ~5.5-6% peak. BoE peaked at 5.25%. BlackRock was correct that market pricing was too hawkish.",
        "assessment": "correct", "qualitative": True
    },
    # BlackRock 2022 midyear: US 10y yield "rising further as term premium restored"
    "blackrock_2022_midyear.json_2": {
        "actual_value": 3.88, "actual_source": "FRED DGS10",
        "note": "10y yield was ~2.98% in Jun 2022, rose to 3.88% by year-end. Correct: yields did rise.",
        "assessment": "correct", "qualitative": True
    },
    # BlackRock 2023: Core CPI 2023-2025 "persistently above 2%"
    "blackrock_2023.json_1": {
        "actual_value": "Core CPI: 4.8% (2023), 3.3% (2024) - stayed above 2%",
        "actual_source": "BLS",
        "note": "Core CPI remained well above 2% through 2024. Correct assessment.",
        "assessment": "correct", "qualitative": True
    },
    # BlackRock 2021: 5-year CPI forward 2025-2030: not verifiable yet
    "blackrock_2021.json_1": {
        "actual_value": "Not yet verifiable (forecast period 2025-2030)",
        "actual_source": "N/A",
        "note": "This is a medium-term forecast for 2025-2030. Cannot be fully scored yet.",
        "assessment": "not_verifiable", "qualitative": True
    },
    # JPM 2018: Long-term govt bond yields "grind slightly higher"
    "jpmorgan_am_2018.json_2": {
        "actual_value": "US 10y: 2.69% (end-2018), up from 2.41% (end-2017)",
        "actual_source": "FRED DGS10",
        "note": "Yields did grind higher in 2018 overall, though volatile. Correct directionally.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2021: GDP trajectory H1 vs H2
    "jpmorgan_am_2021.json_0": {
        "actual_value": "Q1: 6.3%, Q2: 6.7%, Q3: 2.3%, Q4: 6.9% (annualized)",
        "actual_source": "BEA",
        "note": "GDP was strong in H1 but slowed in Q3 before rebounding in Q4. Partially correct: H1 was not 'depressed'.",
        "assessment": "partially_correct", "qualitative": True
    },
    # JPM 2022: Wage growth "remain high"
    "jpmorgan_am_2022.json_7": {
        "actual_value": "Average hourly earnings grew 4.6% YoY in 2022",
        "actual_source": "BLS",
        "note": "Wage growth remained elevated at ~4.6% in 2022. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2024: Wage inflation "decline"
    "jpmorgan_am_2024.json_3": {
        "actual_value": "Average hourly earnings grew 3.9% YoY in 2024 (down from 4.1% in 2023)",
        "actual_source": "BLS",
        "note": "Wage inflation did decline modestly. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # UBS IG credit spread June 2021
    "ubs_2021.json_4": {
        "actual_value": 80, "actual_source": "Bloomberg US Agg Corporate OAS",
        "note": "US IG OAS was approximately 80 bps in June 2021. Forecast was spot-on."
    },
    # UBS EUR/USD June 2021
    "ubs_2021.json_7": {
        "actual_value": 1.186, "actual_source": "Bloomberg",
        "note": "EUR/USD was ~1.186 at end of June 2021"
    },
    # UBS European equity earnings growth 2023
    "ubs_2023.json_1": {
        "actual_value": "Euro Stoxx 600 EPS fell ~3% in 2023",
        "actual_source": "FactSet / Bloomberg",
        "note": "European earnings declined but less than the -10% forecast. Correct direction, magnitude off.",
        "assessment": "partially_correct", "qualitative": True
    },
    # UBS Asian equity earnings growth 2023
    "ubs_2023.json_2": {
        "actual_value": "MSCI Asia ex-Japan EPS declined ~5% in 2023",
        "actual_source": "MSCI / FactSet",
        "note": "Asian earnings actually declined in 2023 vs +2% forecast. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # Morgan Stanley Gold 2019 - $1,500 target
    "morgan_stanley_im_2019.json_0": {
        "actual_value": 1517, "actual_source": "LBMA",
        "note": "Gold ended 2019 at $1,517/oz. Forecast of $1,500 was very close."
    },
    # UBS Chinese yuan trade-weighted 2019 (5% decline)
    "ubs_2019.json_2": {
        "actual_value": "CNY depreciated ~1.5% trade-weighted in 2019",
        "actual_source": "BIS / CFETS",
        "note": "Yuan declined less than forecast 5%. Forecast was directionally correct but magnitude too large.",
        "assessment": "partially_correct", "qualitative": True
    },
    # --- Qualitative predictions that need manual scoring ---
    # BlackRock 2019: pickup in global growth
    "blackrock_2019.json_0": {
        "actual_value": 2.8, "actual_source": "IMF WEO",
        "note": "Global GDP slowed from 3.6% in 2018 to 2.8% in 2019. Forecast of 'pickup' was incorrect - growth slowed.",
        "assessment": "incorrect", "qualitative": True
    },
    # BlackRock 2020 midyear: cumulative GDP shortfall
    "blackrock_2020_midyear.json_0": {
        "actual_value": "US GDP recovered to pre-Covid level by Q2 2021",
        "actual_source": "BEA",
        "note": "US GDP shortfall was indeed smaller than the GFC recovery. Correct assessment.",
        "assessment": "correct", "qualitative": True
    },
    # BlackRock 2020 midyear: Euro area Q4 contraction
    "blackrock_2020_midyear.json_1": {
        "actual_value": -6.1, "actual_source": "Eurostat",
        "note": "Eurozone GDP contracted -6.1% in 2020 (published mid-2020, saw contraction coming). Correct.",
        "assessment": "correct", "qualitative": True
    },
    # BlackRock 2021: full economic restart by late 2021
    "blackrock_2021.json_0": {
        "actual_value": 5.9, "actual_source": "BEA",
        "note": "US real GDP surpassed pre-Covid level by Q2 2021. Correct - full restart achieved.",
        "assessment": "correct", "qualitative": True
    },
    # BlackRock 2024: 10y yield neutral/equal odds
    "blackrock_2024.json_2": {
        "actual_value": 4.58, "actual_source": "FRED DGS10",
        "note": "10y yield was ~3.88% end-2023, rose to 4.58% end-2024. Yields moved higher, not neutral.",
        "assessment": "partially_correct", "qualitative": True
    },
    # BlackRock 2024: BOJ wind down ultra-loose
    "blackrock_2024.json_4": {
        "actual_value": 0.25, "actual_source": "Bank of Japan",
        "note": "BOJ ended negative rates in Mar 2024, hiked to 0.25% in Jul 2024. Correct - ultra-loose policy was wound down.",
        "assessment": "correct", "qualitative": True
    },
    # Fidelity 2024: Fed rates peaked
    "fidelity_2024.json_4": {
        "actual_value": "Fed held at 5.25-5.50% then cut in Sep 2024",
        "actual_source": "Federal Reserve",
        "note": "Rates had indeed peaked at 5.25-5.50% (last hike Jul 2023). Correct.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2022: Goods price inflation will fall
    "jpmorgan_am_2022.json_6": {
        "actual_value": "Goods CPI decelerated from ~12% early 2022 to ~2% by end-2022",
        "actual_source": "BLS",
        "note": "Goods inflation did fall significantly as supply chains eased. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2023: Durable goods deflation
    "jpmorgan_am_2023.json_5": {
        "actual_value": "Durable goods CPI turned negative (-1.1% YoY) by early 2023",
        "actual_source": "BLS",
        "note": "Durable goods did enter deflation. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2023: Core shelter inflation dampen
    "jpmorgan_am_2023.json_6": {
        "actual_value": "Shelter CPI peaked at 8.2% Mar 2023, fell to 6.2% by Dec 2023",
        "actual_source": "BLS",
        "note": "Shelter inflation did slow from peak but remained elevated. Partially correct - dampened but not substantially.",
        "assessment": "partially_correct", "qualitative": True
    },
    # JPM 2023: Overall inflation slow meaningfully
    "jpmorgan_am_2023.json_7": {
        "actual_value": 4.1, "actual_source": "BLS CPI-U annual average",
        "note": "CPI fell from 8.0% (2022) to 4.1% (2023). Inflation did slow meaningfully. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # MS 2019: S&P 500 bear market resumption
    "morgan_stanley_im_2019.json_5": {
        "actual_value": 3231, "actual_source": "Bloomberg (S&P 500 year-end 2019)",
        "note": "S&P 500 rallied +29% in 2019 (2507 to 3231). No bear market. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # Vanguard 2020: BoE on hold
    "vanguard_2020.json_8": {
        "actual_value": 0.10, "actual_source": "Bank of England",
        "note": "BoE cut from 0.75% to 0.10% in Mar 2020 due to Covid. 'On hold' was incorrect - rates were cut sharply.",
        "assessment": "incorrect", "qualitative": True
    },
    # Vanguard 2024: mild downturn expected
    "vanguard_2024.json_4": {
        "actual_value": 2.8, "actual_source": "BEA",
        "note": "US GDP grew 2.8% in 2024. No downturn occurred. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # Fidelity 2021 midyear: Eurozone growth higher in 2022 than 2021
    "fidelity_2021_midyear.json_1": {
        "actual_value": "2021: 5.9%, 2022: 3.4%",
        "actual_source": "Eurostat",
        "note": "Eurozone GDP growth was lower in 2022 (3.4%) than 2021 (5.9%). Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # Fidelity 2023: Eurozone recession before US
    "fidelity_2023.json_1": {
        "actual_value": 0.4, "actual_source": "Eurostat",
        "note": "Eurozone grew 0.4% in 2023 - no recession (though very weak). Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # Fidelity 2023: Eurozone downside risk vs -0.1% consensus
    "fidelity_2023.json_4": {
        "actual_value": 0.4, "actual_source": "Eurostat",
        "note": "Eurozone grew 0.4% in 2023, beating the -0.1% consensus. Downside risk did not materialize. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # Fidelity 2022 midyear: Eurozone recession within next year
    "fidelity_2022_midyear.json_1": {
        "actual_value": "Eurozone: 3.4% (2022), 0.4% (2023) - no technical recession",
        "actual_source": "Eurostat",
        "note": "Eurozone avoided recession through mid-2023 despite very weak growth. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # Fidelity 2018: S&P 500 end of decade target 2700 (horizon is end 2019)
    "fidelity_2018.json_0": {
        "actual_value": 3231, "actual_source": "Bloomberg (S&P 500)",
        "note": "S&P 500 ended 2019 at 3,231 vs forecast of 2,700. Too low by 531 points."
    },
    # --- Fix cross-unit and timing mismatches ---
    # Amundi MSCI Europe index (our ref table has MSCI Europe Net in different scale ~140-170, Amundi uses price ~1800-2000)
    "amundi_2022.json_22": {
        "actual_value": 1829, "actual_source": "MSCI Europe Price Index (approx)",
        "note": "MSCI Europe Price Index ended Nov 2022 at ~1,829 vs forecast 1,940-2,120. Too high by ~151 points."
    },
    "amundi_2024.json_38": {
        "actual_value": 2134, "actual_source": "MSCI Europe Price Index (approx end-2024)",
        "note": "MSCI Europe Price Index ended Q4 2024 at ~2,134 vs forecast 1,780-2,000. Too low by ~244 points."
    },
    # Amundi timing predictions - fix wrong event key matches
    "amundi_2024.json_20": {
        "actual_value": "September 18, 2024",
        "actual_source": "Federal Reserve",
        "note": "Fed's first rate cut was Sep 18, 2024. Amundi predicted May/June 2024 — about 3-4 months early.",
        "assessment": "partially_correct", "qualitative": True
    },
    "amundi_2024.json_24": {
        "actual_value": "June 6, 2024",
        "actual_source": "ECB",
        "note": "ECB first cut was June 6, 2024. Amundi predicted June 2024 — essentially correct.",
        "assessment": "correct", "qualitative": True
    },
    # Amundi ECB rate cuts in 2024 (125bp forecast)
    "amundi_2024.json_23": {
        "actual_value": "100bp of cuts in 2024 (Jun 25bp, Sep 25bp, Oct 25bp, Dec 25bp)",
        "actual_source": "ECB",
        "note": "ECB cut 100bp in 2024 vs 125bp forecast. Close but slightly too aggressive.",
        "assessment": "partially_correct", "qualitative": True
    },
    # Amundi Fed rate cuts in 2024 (150bp forecast)
    "amundi_2024.json_19": {
        "actual_value": "100bp of cuts (Sep 50bp, Nov 25bp, Dec 25bp)",
        "actual_source": "Federal Reserve",
        "note": "Fed cut 100bp in 2024 vs 150bp forecast. Overestimated easing by 50bp.",
        "assessment": "partially_correct", "qualitative": True
    },
    # BlackRock ECB "no rate rise until after mid-2019" — it was correct, no hike happened
    "blackrock_2018_midyear.json_0": {
        "actual_value": "ECB deposit rate stayed at -0.40% through mid-2019 (cut to -0.50% Sep 2019)",
        "actual_source": "ECB",
        "note": "Correct — ECB did not raise rates until July 2022. Deposit rate was -0.40% through mid-2019.",
        "assessment": "correct", "qualitative": True
    },
    # BlackRock 2023: Fed stops hiking in 2023
    "blackrock_2023.json_2": {
        "actual_value": "Fed's last hike was July 2023 (to 5.25-5.50%)",
        "actual_source": "Federal Reserve",
        "note": "Correct — Fed stopped hiking in July 2023 and held at 5.25-5.50%. Activity did stabilize, and inflation stayed above 2%.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2018 ECB "no rate rise in 2018; first rate rise in 2019"
    "jpmorgan_am_2018.json_1": {
        "actual_value": "ECB main refi stayed at 0.00% throughout 2018 and 2019 (no hike until July 2022)",
        "actual_source": "ECB",
        "note": "Correct that no rate rise in 2018. But first rate rise was not in 2019 — it was July 2022. Partially correct.",
        "assessment": "partially_correct", "qualitative": True
    },
    # JPM 2019 Fed hikes (at least one then pause)
    "jpmorgan_am_2019.json_1": {
        "actual_value": "Fed cut 3 times in 2019 (Jul, Sep, Oct) to 1.50-1.75%",
        "actual_source": "Federal Reserve",
        "note": "Predicted at least one hike then pause. Instead Fed cut 3 times. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # JPM 2020 payroll gains — was matched to unemployment rate (wrong)
    "jpmorgan_am_2020.json_4": {
        "actual_value": "Average -774K/month in 2020 (massive losses from Covid)",
        "actual_source": "BLS",
        "note": "Predicted ~130K/month gains. Covid caused massive losses instead. Incorrect (unforeseeable).",
        "assessment": "incorrect", "qualitative": True
    },
    # JPM 2020 real disposable income — was matched to GDP (wrong)
    "jpmorgan_am_2020.json_5": {
        "actual_value": "Real disposable income grew ~6.2% in 2020 (boosted by stimulus payments)",
        "actual_source": "BEA",
        "note": "Predicted ~2% growth. Actual was ~6.2% due to massive fiscal stimulus. Incorrect — growth was much higher.",
        "assessment": "too_low", "qualitative": True
    },
    # JPM 2020 federal budget deficit
    "jpmorgan_am_2020.json_8": {
        "actual_value": "$3.1 trillion deficit in FY2020",
        "actual_source": "CBO / Treasury",
        "note": "Predicted >$1 trillion. Actual was $3.1 trillion due to Covid spending. Correct direction but magnitude vastly underestimated.",
        "assessment": "partially_correct", "qualitative": True
    },
    # JPM 2020 S&P 500 EPS growth 1-2.5%
    "jpmorgan_am_2020.json_9": {
        "actual_value": -14.1, "actual_source": "S&P / FactSet",
        "note": "Predicted 1-2.5% EPS growth. Actual was -14.1% (Covid). Forecast was too high."
    },
    # JPM 2022 S&P 500 total return 7-10% → should compare to S&P return not index level
    "jpmorgan_am_2022.json_1": {
        "actual_value": "-18.1% total return",
        "actual_source": "Bloomberg (S&P 500 TR)",
        "note": "Predicted 7-10% total return. Actual was -18.1%. Forecast was too high by ~26 percentage points.",
        "assessment": "too_high", "qualitative": True
    },
    # JPM 2022 S&P profit margins
    "jpmorgan_am_2022.json_2": {
        "actual_value": "Net margins compressed ~1% from peak in 2022",
        "actual_source": "FactSet",
        "note": "Predicted margins would fall ~1% to 2017-2019 levels. Margins did compress but not back to pre-pandemic levels. Partially correct.",
        "assessment": "partially_correct", "qualitative": True
    },
    # JPM 2022 Brent oil average $80-90
    "jpmorgan_am_2022.json_4": {
        "actual_value": 99.0, "actual_source": "ICE (Brent annual average 2022)",
        "note": "Predicted $80-$90 average. Actual was ~$99 (Russia-Ukraine war). Too low."
    },
    # JPM 2022 oil demand (mbd vs matched to brent price)
    "jpmorgan_am_2022.json_5": {
        "actual_value": "Global oil demand ~99.4 mbd in 2022",
        "actual_source": "IEA",
        "note": "Predicted demand reaching 99.8 mbd. Actual was ~99.4 mbd. Very close.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2022 oil demand 2023 avg 101.5 mbd
    "jpmorgan_am_2022.json_6": {
        "actual_value": "Global oil demand ~101.0 mbd in 2023",
        "actual_source": "IEA",
        "note": "Predicted 101.5 mbd. Actual was ~101.0 mbd. Very close.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2023 S&P 500 earnings decline 10-15%
    "jpmorgan_am_2023.json_2": {
        "actual_value": "S&P 500 EPS grew ~0.9% in 2023",
        "actual_source": "S&P / FactSet",
        "note": "Predicted 10-15% EPS decline. Actual was slight growth (+0.9%). Forecast was too bearish.",
        "assessment": "incorrect", "qualitative": True
    },
    # JPM 2023 S&P bottom in H1 2023
    "jpmorgan_am_2023.json_3": {
        "actual_value": "S&P 500 bottomed at 3,808 in Oct 2022 (already behind by publication). Rose throughout 2023.",
        "actual_source": "Bloomberg",
        "note": "October 2022 lows did hold. S&P rallied through 2023. Correct that Oct lows held.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2024 S&P earnings growth "single-digit"
    "jpmorgan_am_2024.json_0": {
        "actual_value": "S&P 500 EPS grew ~8.6% in 2024",
        "actual_source": "S&P / FactSet",
        "note": "Predicted single-digit growth. Actual was 8.6% — technically single-digit. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2024 10y yield "fluctuate 4-5%"
    "jpmorgan_am_2024.json_2": {
        "actual_value": "10y yield ranged 3.62%-4.74% in 2024, ended at 4.58%",
        "actual_source": "FRED DGS10",
        "note": "Predicted 4-5% range. Actual range was 3.62-4.74%, mostly within the predicted band. Largely correct.",
        "assessment": "correct", "qualitative": True
    },
    # MS 2019 Fed rate hiking cycle
    "morgan_stanley_im_2019.json_4": {
        "actual_value": "Fed paused in Jan 2019, then cut 3 times (Jul/Sep/Oct)",
        "actual_source": "Federal Reserve",
        "note": "Correctly predicted pause in hiking cycle. Fed did pause then reversed to cuts.",
        "assessment": "correct", "qualitative": True
    },
    # MS 2019 S&P EPS negative by Q4 2019
    "morgan_stanley_im_2019.json_3": {
        "actual_value": "S&P 500 EPS grew ~1.2% full-year 2019 (Q4 was ~2% YoY)",
        "actual_source": "S&P / FactSet",
        "note": "Predicted negative EPS growth by Q4. Actual was slightly positive. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # MS 2018 Fed funds rate direction "continued increases at roughly same pace (three hikes)"
    "morgan_stanley_im_2018.json_4": {
        "actual_value": "Fed hiked 4 times in 2018 (to 2.25-2.50%)",
        "actual_source": "Federal Reserve",
        "note": "Predicted 3 hikes. Fed actually hiked 4 times. Correct direction, slightly underestimated.",
        "assessment": "partially_correct", "qualitative": True
    },
    # MS 2023 TOPIX +11% return (was being compared to index level)
    "morgan_stanley_im_2023.json_4": {
        "actual_value": "+25.1% return (TOPIX rose from 1891 to 2366)",
        "actual_source": "JPX",
        "note": "Predicted +11% return. Actual was +25.1%. Correct direction but underestimated by 14pp.",
        "assessment": "too_low", "qualitative": True
    },
    # MS 2022 S&P 500 return -5% (price return vs matched to index level)
    "morgan_stanley_im_2022.json_0": {
        "actual_value": "-19.4% price return",
        "actual_source": "Bloomberg (S&P 500)",
        "note": "Predicted -5% decline. Actual was -19.4%. Correct direction but underestimated severity.",
        "assessment": "partially_correct", "qualitative": True
    },
    # MS 2022 TOPIX +12% (return vs level)
    "morgan_stanley_im_2022.json_1": {
        "actual_value": "-5.1% price return (TOPIX declined from 1992 to 1891)",
        "actual_source": "JPX",
        "note": "Predicted +12% return. Actual was -5.1%. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # MS 2022 MSCI Europe +8% return
    "morgan_stanley_im_2022.json_2": {
        "actual_value": "-14.5% price return",
        "actual_source": "MSCI",
        "note": "Predicted +8% return. Actual was -14.5%. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },
    # MS 2023 TOPIX +11%
    "morgan_stanley_im_2023.json_5": {
        "actual_value": "+25.1% price return (TOPIX rose from 1891 to 2366)",
        "actual_source": "JPX",
        "note": "Predicted +11%. Actual was +25.1%. Correct direction but underestimated by 14pp.",
        "assessment": "too_low", "qualitative": True
    },
    # MS 2023 MSCI EM +12%
    "morgan_stanley_im_2023.json_6": {
        "actual_value": "+7.1% price return (MSCI EM rose from 956 to 1024)",
        "actual_source": "MSCI",
        "note": "Predicted +12%. Actual was ~+7%. Correct direction but overestimated.",
        "assessment": "too_high", "qualitative": True
    },
    # MS 2023 MSCI Europe 6.3% total return
    "morgan_stanley_im_2023.json_7": {
        "actual_value": "+14.3% price return (MSCI Europe rose from 140 to 160)",
        "actual_source": "MSCI",
        "note": "Predicted 6.3% total return. Actual was ~15.4% total return. Correct direction, underestimated.",
        "assessment": "too_low", "qualitative": True
    },
    # MS 2024 Fed first cut "June 2024" (pred index 2)
    "morgan_stanley_im_2024.json_2": {
        "actual_value": "September 18, 2024",
        "actual_source": "Federal Reserve",
        "note": "Predicted June 2024 rate cut. Actual was September 2024. About 3 months early.",
        "assessment": "partially_correct", "qualitative": True
    },
    # MS 2024 ECB first cut "June 2024" (pred index 3)
    "morgan_stanley_im_2024.json_3": {
        "actual_value": "June 6, 2024",
        "actual_source": "ECB",
        "note": "Predicted June 2024 ECB cut. Actual was June 6, 2024. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # MS 2024 Fed first cut (pred index 4 - duplicate key check)
    "morgan_stanley_im_2024.json_4": {
        "actual_value": "September 18, 2024",
        "actual_source": "Federal Reserve",
        "note": "Predicted June 2024 rate cut. Actual was September 2024. About 3 months early.",
        "assessment": "partially_correct", "qualitative": True
    },
    # MS 2024 ECB first cut "June 2024"
    "morgan_stanley_im_2024.json_5": {
        "actual_value": "June 6, 2024",
        "actual_source": "ECB",
        "note": "Predicted June 2024 ECB cut. Actual was June 6, 2024. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # BlackRock 2019 Fed one additional 25bp cut
    "blackrock_2019.json_1": {
        "actual_value": "Fed cut 3 times in H2 2019 (75bp total, to 1.50-1.75%)",
        "actual_source": "Federal Reserve",
        "note": "Predicted one 25bp cut. Fed actually cut 3 times (75bp). Correct direction but underestimated.",
        "assessment": "partially_correct", "qualitative": True
    },
    # UBS 2023 Fed final hike timing
    "ubs_2023.json_3": {
        "actual_value": "Fed's last hike was July 26, 2023 (to 5.25-5.50%)",
        "actual_source": "Federal Reserve",
        "note": "Predicted final hike by Q1 or Q2 2023 at latest. Actual last hike was July 2023. Close but slightly late.",
        "assessment": "partially_correct", "qualitative": True
    },
    # UBS 2023 ECB final hike timing
    "ubs_2023.json_4": {
        "actual_value": "ECB's last hike was September 14, 2023 (to 4.00%)",
        "actual_source": "ECB",
        "note": "Predicted final hike by Q1 or Q2 2023. Actual last hike was Sep 2023. Incorrect — too early by 2 quarters.",
        "assessment": "incorrect", "qualitative": True
    },
    # UBS 2023 BoE final hike timing
    "ubs_2023.json_5": {
        "actual_value": "BoE's last hike was August 3, 2023 (to 5.25%)",
        "actual_source": "Bank of England",
        "note": "Predicted final hike by Q1 or Q2 2023. Actual last hike was Aug 2023. Incorrect — too early by ~2 quarters.",
        "assessment": "incorrect", "qualitative": True
    },
    # UBS 2021 HY credit spread June 2021 (was matched to IG instead of HY)
    "ubs_2021.json_5": {
        "actual_value": 271, "actual_source": "Bloomberg US HY OAS (approx Jun 2021)",
        "note": "US HY OAS was ~271 bps in June 2021 vs forecast of 400 bps. Forecast too high."
    },
    # UBS 2021 EMBIG spread June 2021
    "ubs_2021.json_6": {
        "actual_value": 333, "actual_source": "JPM EMBI Global (approx Jun 2021)",
        "note": "EMBIG spread was ~333 bps in June 2021 vs forecast of 340 bps. Very close."
    },
    # Vanguard Fed rate cuts (pred index 6, matched wrong event)
    "vanguard_2020.json_6": {
        "actual_value": "Fed cut from 1.50-1.75% to 0-0.25% in March 2020 (150bp emergency cuts)",
        "actual_source": "Federal Reserve",
        "note": "Predicted 1-2 cuts (25-50bp). Fed cut 150bp in emergency moves due to Covid. Correct direction, vastly underestimated.",
        "assessment": "partially_correct", "qualitative": True
    },
    # Vanguard 2020 Fed rate cuts (pred index 7)
    "vanguard_2020.json_7": {
        "actual_value": "Fed cut from 1.50-1.75% to 0-0.25% in March 2020 (150bp emergency cuts)",
        "actual_source": "Federal Reserve",
        "note": "Predicted 1-2 cuts (25-50bp). Fed cut 150bp in emergency moves due to Covid. Correct direction, vastly underestimated.",
        "assessment": "partially_correct", "qualitative": True
    },
    # Vanguard 2022 Fed first hike timing "H2 2022"
    "vanguard_2022.json_9": {
        "actual_value": "March 16, 2022",
        "actual_source": "Federal Reserve",
        "note": "Predicted first hike in H2 2022. Actual was March 2022. Forecast was about 6 months late.",
        "assessment": "incorrect", "qualitative": True
    },
    # Vanguard 2022 BoE first rate hike "December 2021"
    "vanguard_2022.json_12": {
        "actual_value": "December 16, 2021",
        "actual_source": "Bank of England",
        "note": "Predicted December 2021 (or Feb 2022). BoE hiked December 16, 2021. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # Vanguard 2022 ECB "no rate hikes for 24 months"
    "vanguard_2022.json_11": {
        "actual_value": "ECB hiked in July 2022 (about 7 months after publication)",
        "actual_source": "ECB",
        "note": "Predicted no hikes for 24 months. ECB hiked in July 2022 — just 7 months later. Incorrect.",
        "assessment": "incorrect", "qualitative": True
    },

    # Vanguard 2024 Fed rate cut timing "second half of 2024"
    "vanguard_2024.json_13": {
        "actual_value": "September 18, 2024",
        "actual_source": "Federal Reserve",
        "note": "Predicted H2 2024. Fed's first cut was September 18, 2024. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2024 median S&P 500 stock return single-digit
    "jpmorgan_am_2024.json_1": {
        "actual_value": "S&P 500 equal-weight returned ~13% in 2024",
        "actual_source": "Bloomberg",
        "note": "Equal-weight S&P 500 returned ~13% in 2024. Single-digit forecast was too low.",
        "assessment": "too_low", "qualitative": True
    },
    # JPM 2024: Fed funds cuts less than 140bps
    "jpmorgan_am_2024.json_4": {
        "actual_value": "100bps of cuts (Sep 50bp + Nov 25bp + Dec 25bp)",
        "actual_source": "Federal Reserve",
        "note": "Fed cut 100bps total in 2024, indeed less than the 140bps market was pricing. Correct.",
        "assessment": "correct", "qualitative": True
    },
    # JPM 2024: GDP slowing but no sharp decline
    "jpmorgan_am_2024.json_5": {
        "actual_value": 2.8, "actual_source": "BEA",
        "note": "US GDP grew 2.8% in 2024. Correct that there was no sharp decline, though growth barely slowed (2.5% in 2023).",
        "assessment": "correct", "qualitative": True
    },
}


def score_one(pred, ref):
    """Score a single prediction."""
    result = {
        "company": pred["company"],
        "report_year": pred["report_year"],
        "publication_date": pred["publication_date"],
        "category": pred.get("category", ""),
        "region": pred.get("region", ""),
        "description": build_description(pred),
        "variable": pred.get("variable", ""),
        "forecast_value": pred.get("forecast_value", ""),
        "horizon": pred.get("horizon", ""),
        "source_quote": pred.get("source_quote", ""),
        "actual_value": None,
        "actual_source": "",
        "verification_confidence": "unmatched",
        "error_direction": "",
        "error_magnitude": None,
        "error_pct": None,
        "result_summary": "",
        "matched_ref_key": "",
        "pred_id": pred["pred_id"],
    }

    # Check manual lookups first
    pid = pred["pred_id"]
    if pid in MANUAL_ACTUALS:
        m = MANUAL_ACTUALS[pid]
        result["actual_value"] = m["actual_value"]
        result["actual_source"] = m.get("actual_source", "")
        result["matched_ref_key"] = "manual_lookup"

        if m.get("qualitative"):
            assessment = m.get("assessment", "qualitative")
            result["verification_confidence"] = "medium"
            result["error_direction"] = assessment
            result["result_summary"] = (
                f"{pred['company']} predicted {pred['variable']} for {pred['region']} "
                f"at {pred['horizon']} would be {pred['forecast_value']}. "
                f"Actual: {m['actual_value']} ({m['actual_source']}). {m.get('note', '')}"
            )
        else:
            result["verification_confidence"] = "high"
            forecast_num = parse_number(pred.get("forecast_value", ""))
            actual_num = m["actual_value"] if isinstance(m["actual_value"], (int, float)) else parse_number(str(m["actual_value"]))
            if forecast_num is not None and actual_num is not None:
                error, magnitude, pct = compute_error(forecast_num, actual_num)
                direction = determine_direction(error)
                result["error_direction"] = direction
                result["error_magnitude"] = round(magnitude, 2) if magnitude is not None else None
                result["error_pct"] = round(pct, 1) if pct is not None else None
                result["result_summary"] = build_result_summary(
                    pred, actual_num, m["actual_source"], direction, magnitude, forecast_num, "manual_lookup"
                )
            else:
                result["result_summary"] = (
                    f"{pred['company']} predicted {pred['variable']} for {pred['region']} "
                    f"at {pred['horizon']} would be {pred['forecast_value']}. "
                    f"Actual: {m['actual_value']} ({m['actual_source']}). {m.get('note', '')}"
                )
        return result

    # Try timing predictions first
    timing = handle_timing_predictions(pred, ref)
    if timing:
        result["actual_value"] = timing["actual_value"]
        result["actual_source"] = timing["actual_source"]
        result["matched_ref_key"] = timing["ref_key"]
        result["verification_confidence"] = "high"

        # Build a summary for timing predictions
        company = pred["company"]
        variable = pred["variable"]
        forecast = pred["forecast_value"]
        actual = timing["actual_value"]
        result["result_summary"] = (
            f"{company} predicted {variable} would be {forecast}. "
            f"Actual: {actual} ({timing['actual_source']})."
        )
        return result

    # Try numeric match against reference table
    actual_val, actual_source, ref_key = try_match(pred, ref)

    forecast_num = parse_number(pred.get("forecast_value", ""))
    qualitative = is_qualitative(pred.get("forecast_value", ""))

    if actual_val is not None:
        result["actual_value"] = actual_val
        result["actual_source"] = actual_source or ""
        result["matched_ref_key"] = ref_key or ""

        if qualitative:
            # Qualitative forecast against numeric actual
            result["verification_confidence"] = "medium"
            q_result, q_note = score_qualitative(pred, actual_val, pred["forecast_value"])
            if q_result == "correct":
                result["error_direction"] = "correct"
                result["result_summary"] = (
                    f"{pred['company']} predicted {pred['variable']} for {pred['region']} "
                    f"at {pred['horizon']} would be {pred['forecast_value']}. "
                    f"Actual was {actual_val} ({actual_source}). {q_note or 'Qualitative match.'}"
                )
            elif q_result == "incorrect":
                result["error_direction"] = "incorrect"
                result["result_summary"] = (
                    f"{pred['company']} predicted {pred['variable']} for {pred['region']} "
                    f"at {pred['horizon']} would be {pred['forecast_value']}. "
                    f"Actual was {actual_val} ({actual_source}). {q_note or 'Qualitative mismatch.'}"
                )
            else:
                result["error_direction"] = "qualitative"
                result["result_summary"] = (
                    f"{pred['company']} predicted {pred['variable']} for {pred['region']} "
                    f"at {pred['horizon']} would be {pred['forecast_value']}. "
                    f"Actual was {actual_val} ({actual_source}). Qualitative prediction - manual review needed."
                )
        else:
            # Numeric forecast against numeric actual
            result["verification_confidence"] = "high"
            if forecast_num is not None:
                error, magnitude, pct = compute_error(forecast_num, actual_val)
                direction = determine_direction(error)
                result["error_direction"] = direction
                result["error_magnitude"] = round(magnitude, 2) if magnitude is not None else None
                result["error_pct"] = round(pct, 1) if pct is not None else None
                result["result_summary"] = build_result_summary(
                    pred, actual_val, actual_source, direction, magnitude, forecast_num, ref_key or ""
                )
            else:
                result["result_summary"] = (
                    f"{pred['company']} predicted {pred['variable']} for {pred['region']} "
                    f"at {pred['horizon']} would be {pred['forecast_value']}. "
                    f"Actual was {actual_val} ({actual_source}). Could not parse forecast for numeric comparison."
                )
                result["verification_confidence"] = "low"
    else:
        # No match found
        result["verification_confidence"] = "unmatched"
        result["result_summary"] = (
            f"{pred['company']} predicted {pred['variable']} for {pred['region']} "
            f"at {pred['horizon']} would be {pred['forecast_value']}. "
            f"No matching actual data in reference table - needs manual lookup."
        )

    return result


def main():
    ref = load_reference()
    preds = load_all_predictions()
    print(f"Loaded {len(preds)} predictions from {len(set(p['file'] for p in preds))} files")

    scored = []
    matched = 0
    unmatched = 0
    qualitative = 0

    for pred in preds:
        result = score_one(pred, ref)
        scored.append(result)

        if result["verification_confidence"] == "unmatched":
            unmatched += 1
        elif result["verification_confidence"] in ("high", "medium"):
            matched += 1
        else:
            qualitative += 1

    print(f"\nResults:")
    print(f"  Matched (high/medium confidence): {matched}")
    print(f"  Unmatched (needs lookup): {unmatched}")
    print(f"  Low confidence: {qualitative}")

    # Save results
    output_file = os.path.join(OUTPUT_DIR, "scored_predictions.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(scored, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {output_file}")

    # Print summary by company
    print("\n--- By Company ---")
    companies = {}
    for r in scored:
        c = r["company"]
        if c not in companies:
            companies[c] = {"total": 0, "matched": 0, "unmatched": 0}
        companies[c]["total"] += 1
        if r["verification_confidence"] in ("high", "medium"):
            companies[c]["matched"] += 1
        else:
            companies[c]["unmatched"] += 1
    for c, stats in sorted(companies.items()):
        print(f"  {c}: {stats['matched']}/{stats['total']} matched ({stats['unmatched']} unmatched)")

    # Print unmatched for review
    print("\n--- Unmatched Predictions (need manual lookup) ---")
    for r in scored:
        if r["verification_confidence"] == "unmatched":
            print(f"  [{r['company']} {r['report_year']}] {r['variable']} | {r['region']} | {r['horizon']} | {r['forecast_value']}")


if __name__ == "__main__":
    main()
