
import streamlit as st


def canonical_bucket(name: str) -> str:
    """CSV-first canonicalization, then rollups/rules, else pass-through."""
    import re as _re
    nraw = (name or "").strip()
    n = _re.sub(r"\s+"," ", nraw.lower())

    # CSV overrides first
    try:
        ov = st.session_state.get("__bucket_overrides__", {})
    except Exception:
        ov = {}
    if n in ov:
        chosen = (ov[n] or "").strip()
        if chosen.lower()=="unmapped":
            return nraw
        return chosen

    # ---- Consolidations / rollups ----
    if "guru" in n:
        return "Carguru"

    # Dealer Website Leads wide matches
    if ("do -" in n) or ("di -" in n) or ("ansira" in n) or ("wallingfordbuickgmc.com" in n):
        return "Dealer Website Leads"

    # Dealer Website Leads
    if ("amp" in n) or ("hand-raiser web" in n) or ("interactivetel" in n) or ("wallingford buick gmc - interactivetel" in n):
        return "Dealer Website Leads"

    # Social Media
    if "youtube" in n:
        return "Social Media"

    # GMC.com family
    if ("gmc.com" in n) or (
        "gmc" in n and (
            "offer raq" in n or "build your own" in n or "locate vehicle" in n or "locate a vehicle" in n or "supplier discount" in n
        )
    ):
        return "GMC.com"

    # GM split (strict)
    if ("gm" in n or "gm financial" in n) and "lease" in n:
        return "GM Lease"
    if ("gm" in n or "gm financial" in n) and (("loan" in n) or ("payoff" in n) or ("pay off" in n)):
        return "GM Loan/Payoff"

    # Trade-in ecosystems
    if ("kbb" in n) or ("kelley blue book" in n) or ("instant cash offer" in n) or ("ico" in n) or ("trade pending" in n) or ("tradepending" in n) or ("trade-pending" in n):
        return "Trade In Leads"

    # Marketplaces & others
    if "autotrader" in n or "auto trader" in n: return "AutoTrader"
    if "cars.com" in n or "carscom" in n:     return "Cars.com"
    if "truecar" in n or "true car" in n:     return "TrueCar"
    if "carfax" in n:                         return "CarFax"
    if "autoweb" in n:                        return "Autoweb"
    if "gm 3rd party" in n or "gm third party" in n or "gm 3rd" in n: return "GM Third Party"
    if "shop click drive" in n or n.startswith("scd"):               return "Shop Click Drive"
    if n.startswith("carbravo drp") or "carbravo" in n:              return "CarBravo DRP"

    # Credit / finance
    if "credit" in n or "pre-qual" in n or "prequal" in n or "pre qualification" in n or "finance" in n:
        return "Credit Application"

    if "podium" in n:
        return "Podium"

    return nraw


def canonical_bucket(name: str) -> str:
    raw = (name or "").strip()
    n = re.sub(r"\s+"," ", raw.lower())

    # CSV overrides first
    try:
        ov = st.session_state.get("__bucket_overrides__", {})
    except Exception:
        ov = {}
    if n in ov and ov[n]:
        if ov[n].strip().lower() == "unmapped":
            return raw
        return ov[n].strip()

    # Dealer Website Leads
    if "amp" in n or "hand-raiser web" in n or "interactivetel" in n or "wallingford buick gmc - interactivetel" in n:
        return "Dealer Website Leads"

    # Carguru
    if "guru" in n:
        return "Carguru"

    # GMC.com family
    if "gmc.com" in n:
        return "GMC.com"
    if "gmc" in n and ("offer raq" in n or "build your own" in n or "locate vehicle" in n):
        return "GMC.com"

    # Social Media
    if "youtube" in n: return "Social Media"

    # GM programs
    if ("gm" in n or "gm financial" in n) and "lease" in n:
        return "GM Lease"
    if ("gm" in n or "gm financial" in n) and (("loan" in n) or ("payoff" in n) or ("pay off" in n)):
        return "GM Loan/Payoff"

    # Trade-in ecosystems
    if ("kbb" in n) or ("kelley blue book" in n) or ("instant cash offer" in n) or ("ico" in n) or ("trade pending" in n) or ("tradepending" in n) or ("trade-pending" in n):
        return "Trade In Leads"

    # Marketplaces
    if "autotrader" in n or "auto trader" in n:
        return "AutoTrader"
    if "cars.com" in n or "carscom" in n:
        return "Cars.com"
    if "truecar" in n or "true car" in n:
        return "TrueCar"
    if "carfax" in n:
        return "CarFax"
    if "autoweb" in n:
        return "Autoweb"
    if "gm 3rd party" in n or "gm third party" in n or "gm 3rd" in n:
        return "GM Third Party"
    if "shop click drive" in n or n.startswith("scd"):
        return "Shop Click Drive"
    if n.startswith("carbravo drp") or "carbravo" in n:
        return "CarBravo DRP"

    # Credit Applications
    if "credit" in n or "pre-qual" in n or "prequal" in n or "pre qualification" in n or "finance" in n:
        return "Credit Application"

    if "podium" in n:
        return "Podium"

    return raw

# ===== Lead bucket helpers (v15e) =====
import re as _re, csv, os
def _norm_key(s:str)->str: return _re.sub(r"\s+"," ", (s or "").strip().lower())

def _load_bucket_overrides(path="unmapped_lead_sources.csv"):
    try:
        if not os.path.exists(path): return {}
        ov={}
        with open(path,"r",encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                k=_norm_key(row.get("Lead Source",""))
                b=(row.get("Bucket","") or "").strip()
                if k: ov[k]=b
        return ov
    except Exception:
        return {}

# Make overrides available
try:
    if "__bucket_overrides__" not in st.session_state:
        st.session_state["__bucket_overrides__"]=_load_bucket_overrides()
except Exception:
    pass

NON_INTERNET_SUBSTRINGS = [
    "walk-in","walk in","phone","service","service dept","body shop","parts",
    "bdc outbound","referral","repeat","repeat customer","fleet","event","employee",
    "unknown","record journal","playbook manifest","hill car","drive by","drive-by","drive by - location"
]

def looks_internet(label:str)->bool:
    ss=(str(label) or "").lower()
    subs=NON_INTERNET_SUBSTRINGS
    try:
        subs=[x.lower() for x in st.session_state.get("__non_internet_substrings__", subs)]
    except Exception:
        pass
    return not any(x in ss for x in subs)

def canonical_bucket(name:str)->str:
    """CSV first, then rules; otherwise pass-through raw source."""
    raw=(name or "").strip()
    n=_norm_key(raw)

    # CSV override first
    try:
        ov=st.session_state.get("__bucket_overrides__", {})
    except Exception:
        ov={}
    if n in ov:
        b=(ov[n] or "").strip()
        if b.lower()=="unmapped": return raw  # pass-through
        return b

    # Consolidations / rules
    if "guru" in n: return "Carguru"
    # Dealer Website Leads
    if ("amp" in n) or ("hand-raiser web" in n) or ("interactivetel" in n) or ("interactive tel" in n) or ("wallingford buick gmc - interactivetel" in n):
        return "Dealer Website Leads"
    # GMC.com
    if ("gmc.com" in n) or ("gmc offer raq" in n) or ("gmc build your own" in n) or ("gmc locate vehicle" in n):
        return "GMC.com"
    # Social Media
    if "youtube" in n: return "Social Media"
    # GM Lease strict
    if (("gm" in n) or ("gm financial" in n)) and ("lease" in n):
        return "GM Lease"
    # GM Loan/Payoff strict
    if (("gm" in n) or ("gm financial" in n)) and (("loan" in n) or ("payoff" in n) or ("pay off" in n)):
        return "GM Loan/Payoff"
    # Trade In
    if ("kbb" in n) or ("kelley blue book" in n) or ("instant cash offer" in n) or ("ico" in n) or ("trade pending" in n) or ("tradepending" in n) or ("trade-pending" in n):
        return "Trade In Leads"
    # Marketplaces
    if ("autotrader" in n) or ("auto trader" in n): return "AutoTrader"
    if ("cars.com" in n) or ("carscom" in n): return "Cars.com"
    if ("truecar" in n) or ("true car" in n): return "TrueCar"
    if "carfax" in n: return "CarFax"
    if "autoweb" in n: return "Autoweb"
    if ("gm 3rd party" in n) or ("gm third party" in n) or ("gm 3rd" in n): return "GM Third Party"
    if ("shop click drive" in n) or n.startswith("scd"): return "Shop Click Drive"
    if n.startswith("carbravo drp") or ("carbravo" in n): return "CarBravo DRP"
    # Credit apps
    if ("credit" in n) or ("prequal" in n) or ("pre-qual" in n) or ("pre qualification" in n) or ("finance" in n):
        return "Credit Application"
    # Podium
    if "podium" in n: return "Podium"

    return raw

def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns:
            return c
    return None


def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns:
            return c
    return None



def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns:
            return c
    return None



def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns: return c
    return None

def _ensure_bucket_col(df):
    lead_col = _guess_lead_col(df)
    if lead_col is None:
        if "Bucket" not in df.columns:
            df["Bucket"]="Unknown"
        return df
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # Reinforce Dealer Website Leads
    df.loc[s.str.contains("amp") | s.str.contains("hand-raiser web") | s.str.contains("interactivetel") | s.str.contains("wallingford buick gmc - interactivetel") | s.str.contains("do -") | s.str.contains("di -") | s.str.contains("ansira") | s.str.contains("wallingfordbuickgmc.com"), "Bucket"] = "Dealer Website Leads"

    # Web Chat (includes Podium)
    df.loc[s.str.contains("web chat") | s.str.contains("podium"), "Bucket"] = "Web Chat"

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (s.str.contains("gmc") & (s.str.contains("offer raq") | s.str.contains("build your own") | s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") | s.str.contains("supplier discount")))
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Carguru rollup
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"
    return df


    # Canonical map (CSV first, then rules)
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)

    # Hard re-enforcement for families that often slip (vectorized masks)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (
        s.str.contains("gmc") & (
            s.str.contains("offer raq") | s.str.contains("build your own") |
            s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") |
            s.str.contains("supplier discount")
        )
    )
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # Dealer Website Leads wide mask
    df.loc[s.str.contains("do -") | s.str.contains("di -") | s.str.contains("ansira") | s.str.contains("wallingfordbuickgmc.com"), "Bucket"] = "Dealer Website Leads"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Dealer Website Leads additions
    df.loc[s.str.contains("hand-raiser web") | s.str.contains("interactivetel"), "Bucket"] = "Dealer Website Leads"

    # Social Media
    df.loc[s.str.contains("youtube"), "Bucket"] = "Social Media"

    # Carguru roll-up (safety)
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"

    return df


    # Canonical map (CSV first, then rules)
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)

    # Hard re-enforcement for families that often slip (vectorized masks)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (
        s.str.contains("gmc") & (
            s.str.contains("offer raq") | s.str.contains("build your own") |
            s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") |
            s.str.contains("supplier discount")
        )
    )
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Dealer Website Leads additions
    df.loc[s.str.contains("hand-raiser web") | s.str.contains("interactivetel"), "Bucket"] = "Dealer Website Leads"

    # Social Media
    df.loc[s.str.contains("youtube"), "Bucket"] = "Social Media"

    # Carguru roll-up (safety)
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"

    return df


def looks_internet(source: str) -> bool:
    """Return True if considered Internet (default True unless a non-internet substring hits)."""
    ss = (str(source) or "").lower()
    try:
        import streamlit as _st
        subs = [x.lower() for x in _st.session_state.get("__non_internet_substrings__", NON_INTERNET_SUBSTRINGS)]
    except Exception:
        subs = [x.lower() for x in NON_INTERNET_SUBSTRINGS]
    return not any(sub in ss for sub in subs)

def _norm_key(s:str)->str:
    return _re.sub(r"\s+"," ", (s or "").strip().lower())

def _load_bucket_overrides(path="unmapped_lead_sources.csv"):
    try:
        if not os.path.exists(path): return {}
        ov={}
        with open(path,"r",encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                raw=(row.get("Lead Source") or "").strip()
                bkt=(row.get("Bucket") or "").strip()
                if not raw: continue
                ov[_norm_key(raw)]=bkt
        return ov
    except Exception:
        return {}

try:
    if "__bucket_overrides__" not in st.session_state:
        st.session_state["__bucket_overrides__"]=_load_bucket_overrides()
except Exception:
    # if Streamlit not initialized in this context, ignore
    pass

def canonical_bucket(name: str) -> str:
    """CSV-first canonicalization, then rollups/rules, else pass-through."""
    nraw = (name or "").strip()
    n = _norm_key(nraw)
    # CSV overrides first
    try:
        ov = st.session_state.get("__bucket_overrides__", {})
    except Exception:
        ov = {}
    if n in ov:
        chosen = (ov[n] or "").strip()
        if chosen.lower()=="unmapped":
            return nraw
        return chosen

    # Roll-ups & rules
    if "guru" in n: return "Carguru"
    # AMP -> Dealer Website Leads
    if "amp" in n: return "Dealer Website Leads"
    # GM programs (your rules)
    if ("gm" in n or "gm financial" in n) and "lease" in n:
        return "GM Lease"
    if ("gm" in n or "gm financial" in n) and (("loan" in n) or ("payoff" in n) or ("pay off" in n)):
        return "GM Loan/Payoff"
    # Trade-in ecosystems
    if ("kbb" in n) or ("kelley blue book" in n) or ("instant cash offer" in n) or ("ico" in n)        or ("trade pending" in n) or ("tradepending" in n) or ("trade-pending" in n):
        return "Trade In Leads"
    # Marketplaces
    if "autotrader" in n or "auto trader" in n: return "AutoTrader"
    if "cars.com" in n or "carscom" in n: return "Cars.com"
    if "truecar" in n or "true car" in n: return "TrueCar"
    if "carfax" in n: return "CarFax"
    if "autoweb" in n: return "Autoweb"
    if "gm 3rd party" in n or "gm third party" in n or "gm 3rd" in n: return "GM Third Party"
    if "shop click drive" in n or n.startswith("scd"): return "Shop Click Drive"
    if n.startswith("carbravo drp") or "carbravo" in n: return "CarBravo DRP"
    # Credit Applications (finance terms)
    if ("credit" in n) or ("prequal" in n) or ("pre-qual" in n) or ("pre qualification" in n) or ("finance" in n):
        return "Credit Application"
    if "podium" in n: return "Podium"
    return nraw

def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns:
            return c
    return None


def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns:
            return c
    return None




def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns: return c
    return None

def _ensure_bucket_col(df):
    lead_col = _guess_lead_col(df)
    if lead_col is None:
        if "Bucket" not in df.columns:
            df["Bucket"]="Unknown"
        return df
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # Reinforce Dealer Website Leads
    df.loc[s.str.contains("amp") | s.str.contains("hand-raiser web") | s.str.contains("interactivetel") | s.str.contains("wallingford buick gmc - interactivetel") | s.str.contains("do -") | s.str.contains("di -") | s.str.contains("ansira") | s.str.contains("wallingfordbuickgmc.com"), "Bucket"] = "Dealer Website Leads"

    # Web Chat (includes Podium)
    df.loc[s.str.contains("web chat") | s.str.contains("podium"), "Bucket"] = "Web Chat"

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (s.str.contains("gmc") & (s.str.contains("offer raq") | s.str.contains("build your own") | s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") | s.str.contains("supplier discount")))
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Carguru rollup
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"
    return df


    # Canonical map (CSV first, then rules)
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)

    # Hard re-enforcement for families that often slip (vectorized masks)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (
        s.str.contains("gmc") & (
            s.str.contains("offer raq") | s.str.contains("build your own") |
            s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") |
            s.str.contains("supplier discount")
        )
    )
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # Dealer Website Leads wide mask
    df.loc[s.str.contains("do -") | s.str.contains("di -") | s.str.contains("ansira") | s.str.contains("wallingfordbuickgmc.com"), "Bucket"] = "Dealer Website Leads"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Dealer Website Leads additions
    df.loc[s.str.contains("hand-raiser web") | s.str.contains("interactivetel"), "Bucket"] = "Dealer Website Leads"

    # Social Media
    df.loc[s.str.contains("youtube"), "Bucket"] = "Social Media"

    # Carguru roll-up (safety)
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"

    return df


    # Canonical map
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (
        s.str.contains("gmc") & (
            s.str.contains("offer raq") | s.str.contains("build your own") |
            s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") |
            s.str.contains("supplier discount")
        )
    )
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Dealer Website Leads additions
    df.loc[s.str.contains("hand-raiser web") | s.str.contains("interactivetel"), "Bucket"] = "Dealer Website Leads"

    # Social Media
    df.loc[s.str.contains("youtube"), "Bucket"] = "Social Media"

    # Carguru roll-up (safety)
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"

    return df

# ===================================================

# Paid channel identification
PAID_BUCKETS = set([
    "Carguru", "Cars.com", "AutoTrader", "TrueCar", "CarFax", "Autoweb",
    "GM Third Party", "Trade In Leads", "Podium", "Web Chat"
])

def _ensure_paid_flag(df):
    try:
        import pandas as _pd
        if "__is_paid__" not in df.columns:
            if "Bucket" in df.columns:
                df["__is_paid__"] = df["Bucket"].astype(str).isin(PAID_BUCKETS)
            else:
                s = df.get("Lead Source", _pd.Series([""]*len(df))).astype(str).str.lower()
                paid_subs = ["autotrader","cars.com","carscom","carguru","carfax","autoweb",
                             "truecar","kbb","instant cash offer","ico","trade pending",
                             "tradepending","trade-pending","podium","gm 3rd","gm third","third party"]
                df["__is_paid__"] = s.apply(lambda x: any(t in x for t in paid_subs))
    except Exception:
        pass
    return df


# ---- Monthly Units Goals (default projections) ----
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MONTHLY_UNITS_GOAL = [40, 42, 45, 46, 48, 52, 52, 40, 45, 50, 50, 57]  # Sums to 567

# === Unified Internet source detection ===
NON_INTERNET_SUBSTRINGS = [
    "walk-in", "walk in", "phone", "service", "service dept", "body shop", "parts",
    "bdc outbound", "referral", "repeat", "repeat customer", "fleet", "event", 
    "employee", "unknown", "record journal", "playbook manifest", "hill car",
    "drive by", "drive-by", "drive by - location", "equity", "showroom",
    "phone up", "used car event"
]

def looks_internet(source: str) -> bool:
    """Determine if a lead source should be considered 'internet'.
    Returns True unless a known non-internet keyword is present.
    Respects optional override in st.session_state["__non_internet_substrings__"]."""
    ss = (str(source) or "").lower()
    try:
        subs = [x.lower() for x in st.session_state.get("__non_internet_substrings__", NON_INTERNET_SUBSTRINGS)]
    except Exception:
        subs = [x.lower() for x in NON_INTERNET_SUBSTRINGS]
    return not any(x in ss for x in subs)
# =======================================



# ===== Internet scope helpers (default = internet unless matched) =====
try:
    import streamlit as _st  # use local alias to avoid shadowing
except Exception:
    _st = None

def looks_internet(source: str) -> bool:
    """
    Return True if a lead source string should be considered 'internet'.
    Defaults to True unless a known non-internet keyword is present.
    Never throws NameError (includes its own default list).
    """
    default_substrings = [
        "walk-in", "walk in", "phone", "service", "service dept", "body shop",
        "parts", "bdc outbound", "referral", "repeat", "fleet", "event", "employee"
    ]
    try:
        custom = []
        if _st is not None and hasattr(_st, "session_state"):
            custom = _st.session_state.get("__non_internet_substrings__", [])
        substrings = [s.lower() for s in (custom or default_substrings)]
    except Exception:
        substrings = default_substrings
    s = (str(source) or "").lower()
    return not any(sub in s for sub in substrings)
# =====================================================================



def _roi_to_scale01(roi_series):
    # Convert ROIx to 0..1 with 0 -> 0, 3x -> 0.6, 5x -> 0.8, 10x+ -> 1.0
    import numpy as _np
    v = _np.clip(roi_series.astype(float), 0.0, 10.0)
    # piecewise: 0-3 -> 0..0.6 ; 3-5 -> 0.6..0.8 ; 5-10 -> 0.8..1.0
    out = _np.zeros_like(v, dtype=float)
    m1 = v <= 3.0
    out[m1] = (v[m1] / 3.0) * 0.6
    m2 = (v > 3.0) & (v <= 5.0)
    out[m2] = 0.6 + ((v[m2]-3.0)/(2.0)) * 0.2
    m3 = v > 5.0
    out[m3] = 0.8 + ((v[m3]-5.0)/(5.0)) * 0.2
    return out



# ---- Dynamic Units Goal helper (monthly-aware) ----
def _dynamic_units_goal():
    """Calculate units goal based on selected months and scope."""
    monthly_goals = st.session_state.get("__monthly_goals__", MONTHLY_UNITS_GOAL)
    
    # Get base total from selected months
    base = 0
    mode = st.session_state.get("mode", "Single file")
    
    try:
        if mode == "Single file":
            start_m = st.session_state.get("start_m", "Jan")
            end_m = st.session_state.get("end_m", "Dec")
            si = MONTHS.index(start_m)
            ei = MONTHS.index(end_m)
            if ei < si:
                si, ei = ei, si
            base = sum(monthly_goals[si:ei+1])
        elif mode == "Monthly files":
            selected_months = st.session_state.get("sel", [])
            if selected_months:
                idxs = [MONTHS.index(m) for m in selected_months if m in MONTHS]
                base = sum(monthly_goals[i] for i in sorted(set(idxs)))
            else:
                base = sum(monthly_goals)
        else:
            base = sum(monthly_goals)
    except Exception:
        base = sum(monthly_goals)  # Fallback to full year if anything fails

    # Apply internet ratio if enabled
    # Get the state directly from the toggle in the main interface
    only_internet = bool(st.session_state.get("only_internet", False))
    g = st.session_state.get("__goals__", {"internet_ratio_goal": 0.85})
    
    # Calculate effective goal (apply 85% for internet)
    effective = int(round(base * (g.get("internet_ratio_goal", 0.85) if only_internet else 1.0)))
    
    # Store for display
    st.session_state["__dynamic_units_goal__"] = effective
    st.session_state["__base_units_goal__"] = base
    return effective, base, only_internet



# --- Goals editor (version-compatible) ---
if "__goals__" not in st.session_state:
    st.session_state["__goals__"] = {
        "units_total_goal": 567,
        "internet_ratio_goal": 0.85,
        "sold_rate_goal": 8.5,
        "contact_rate_goal": 50.0,
    }
if "show_goals_editor" not in st.session_state:
    st.session_state["show_goals_editor"] = False

def _goals_form_body():
    g = st.session_state["__goals__"]
    monthly = st.session_state.get("__monthly_goals__", MONTHLY_UNITS_GOAL)
    
    st.markdown("### Annual Goals")
    col1, col2 = st.columns(2)
    with col1:
        internet_ratio = st.slider("% of units from Internet (Only Internet scope)", 0.0, 1.0, float(g["internet_ratio_goal"]))
        sold_goal = st.number_input("Lead → Sale % Goal", min_value=0.0, max_value=100.0, value=float(g["sold_rate_goal"]))
    with col2:
        contact_goal = st.number_input("Contact Rate % Goal", min_value=0.0, max_value=100.0, value=float(g["contact_rate_goal"]))
    
    st.markdown("### Monthly Unit Goals")
    st.caption("Enter the target units for each month. These values will be filtered based on your selected date range.")
    
    # Create 2 rows of 6 months each
    for row in range(2):
        cols = st.columns(6)
        for i in range(6):
            month_idx = row * 6 + i
            with cols[i]:
                monthly[month_idx] = st.number_input(
                    MONTHS[month_idx],
                    min_value=0,
                    value=int(monthly[month_idx]),
                    key=f"month_{month_idx}"
                )
    
    total = sum(monthly)
    st.info(f"Total annual units goal: {total}")
    
    c1, c2 = st.columns(2)
    saved = False
    with c1:
        if st.button("Save", type="primary", key="goals_save_btn"):
            st.session_state["__goals__"].update({
                "internet_ratio_goal": float(internet_ratio),
                "sold_rate_goal": float(sold_goal),
                "contact_rate_goal": float(contact_goal),
            })
            st.session_state["__monthly_goals__"] = monthly
            saved = True
    with c2:
        if st.button("Cancel", key="goals_cancel_btn"):
            st.session_state["show_goals_editor"] = False
            st.rerun()
    if saved:
        st.session_state["show_goals_editor"] = False
        st.rerun()

# Prefer st.dialog (new), else experimental_dialog, else inline fallback container
_edit_dialog_rendered = False
if st.session_state.get("show_goals_editor", False):
    if hasattr(st, "dialog"):
        @st.dialog("Edit YTD Goals")
        def _edit_goals_dialog():
            _goals_form_body()
        _edit_goals_dialog()
        _edit_dialog_rendered = True
    elif hasattr(st, "experimental_dialog"):
        @st.experimental_dialog("Edit YTD Goals")
        def _edit_goals_dialog_exp():
            _goals_form_body()
        _edit_goals_dialog_exp()
        _edit_dialog_rendered = True
    else:
        with st.container(border=True):
            st.markdown("### Edit YTD Goals")
            _goals_form_body()
            st.info("This inline panel is shown because your Streamlit version lacks dialog/modal support.")
        _edit_dialog_rendered = True


# --- Goals state (defaults) ---
if "__goals__" not in st.session_state:
    st.session_state["__goals__"] = {
        "units_total_goal": 567,
        "internet_ratio_goal": 0.85,   # Internet-only share
        "sold_rate_goal": 8.5,         # Lead→Sale % goal
        "contact_rate_goal": 50.0,     # Contact % goal
    }

# --- Modal flag ---
if "show_goals_editor" not in st.session_state:
    st.session_state["show_goals_editor"] = False

if st.session_state["show_goals_editor"]:
    pass
import pandas as pd
import numpy as np
import re
import plotly.express as px


# ---- Monthly Units Goal (defaults; can be edited later) ----
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
# Defaults sum to 567 and cumulative through Jul = 325
MONTHLY_UNITS_GOAL = [40, 42, 45, 46, 48, 52, 52, 40, 45, 50, 50, 57]

def units_goal_for_scope(mode, start_month=None, end_month=None, selected_months=None):
    """Return units goal for the current scope, summing month goals in range or selection."""
    if mode == "Single file" and start_month and end_month:
        si = MONTHS.index(start_month); ei = MONTHS.index(end_month)
        if ei < si: si, ei = ei, si
        return sum(MONTHLY_UNITS_GOAL[si:ei+1])
    elif mode == "Monthly files" and selected_months:
        idxs = [MONTHS.index(m) for m in selected_months if m in MONTHS]
        return sum(MONTHLY_UNITS_GOAL[i] for i in sorted(set(idxs)))
    else:
        return sum(MONTHLY_UNITS_GOAL)


st.set_page_config(page_title="Lead ROI Bubble Map", layout="wide")

# ---------- Global CSS tweaks ----------
st.markdown("""
<style>
/* Sidebar file uploader full width */
section[data-testid="stSidebar"] .stFileUploader { width: 100% !important; }
section[data-testid="stSidebar"] .stFileUploader > div[data-testid="stFileUploaderDropzone"] { width: 100% !important; }
section[data-testid="stSidebar"] .stFileUploader label { font-weight: 700; }
section[data-testid="stSidebar"] .stFileUploader small { opacity:.7; }

/* Scroll container for Top10 */
#top10-scroll {
  height: 820px; /* ~5 full cards + hint of 6th */
  overflow-y: auto;
  padding-right: 8px;
}
/* Nice cards */
.card {
  padding: 12px;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 10px;
  background: rgba(255,255,255,.03);
  margin-bottom: 10px;
}
.badge {
  margin-left:6px;
  padding:2px 8px;
  border-radius:10px;
  background:rgba(255,255,255,.1);
  font-size:11px;
}
.subtle { color:#9aa0a6; }
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def _normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def pct2(x, cap_100=False):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    if cap_100:
        x = min(x, 100.0)
    return "{:.2f}%".format(x)

def num0(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return "{:,.0f}".format(x)

def money0(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return "${:,.0f}".format(x)

def roix_label(v: float) -> str:
    if v is None or (not np.isfinite(v)):
        return "∞x"
    return "{:.2f}x".format(v) if v < 10 else "{:.0f}x".format(v)

def canonical_bucket(name: str) -> str:
    nraw = (name or "").strip()
    n = re.sub(r"\s+", " ", nraw.lower())

    ov = st.session_state.get("__bucket_overrides__", {})
    if ov:
        key = n
        if key in ov:
            chosen = (ov[key] or "").strip()
            if chosen.lower() == "unmapped":
                return nraw
            return chosen

    if "guru" in n:
        return "Carguru"

    if ("kbb" in n) or ("kelley blue book" in n) or ("instant cash offer" in n) or ("ico" in n)        or ("trade pending" in n) or ("tradepending" in n) or ("trade-pending" in n):
        return "Trade In Leads"

    if ("dealer website" in n) or ("gm dealer website" in n) or ("wallingfordgmc.com" in n)        or ("wallingfordbuickgmc.com" in n) or ("wearebuickgmc.com" in n):
        return "Dealer Website Leads"

    if "autotrader" in n or "auto trader" in n:
        return "AutoTrader"
    if "cars.com" in n or "carscom" in n:
        return "Cars.com"
    if "truecar" in n or "true car" in n:
        return "TrueCar"
    if "carfax" in n:
        return "CarFax"
    if "autoweb" in n:
        return "Autoweb"
    if "gm 3rd party" in n or "gm third party" in n or "gm 3rd" in n:
        return "GM Third Party"
    if "shop click drive" in n or n.startswith("scd"):
        return "Shop Click Drive"
    if n.startswith("carbravo drp") or "carbravo" in n:
        return "CarBravo DRP"

    if ("credit" in n) or ("prequal" in n) or ("pre-qual" in n) or ("prequalify" in n) or ("pre qualification" in n) or ("finance" in n):
        return "Credit Application"

    if "podium" in n:
        return "Podium"

    return nraw

def looks_internet(name: str) -> bool:
    n = _normalize_spaces(name)
    return not any(sub in n for sub in NON_INTERNET_SUBSTRINGS)

def read_report(file):
    df = pd.read_excel(file, sheet_name="Report", header=0)
    cols = list(df.columns)
    rename = {}
    keys = ["Lead Source","Total Leads","Sold in Timeframe","Appts Set","Appts Shown"]
    for k in keys:
        if k in df.columns: rename[k]=k
    if "Lead Source" not in rename and len(cols)>0: rename[cols[0]]="Lead Source"
    if "Total Leads" not in rename and len(cols)>1: rename[cols[1]]="Total Leads"
    if "Sold in Timeframe" not in rename and len(cols)>2: rename[cols[2]]="Sold in Timeframe"
    if "Appts Set" not in rename and len(cols)>8: rename[cols[8]]="Appts Set"
    if "Appts Shown" not in rename and len(cols)>10: rename[cols[10]]="Appts Shown"
    df = df.rename(columns=rename)
    try:
        if str(df.iloc[0].get("Lead Source","")).strip().lower()=="lead source":
            df = df.drop(df.index[0]).reset_index(drop=True)
    except Exception: 
        pass
    for c in ["Total Leads","Sold in Timeframe","Appts Set","Appts Shown"]:
        if c not in df.columns: df[c]=0
        df[c]=pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["Bucket"]=df["Lead Source"].astype(str).apply(canonical_bucket)
    df["__internet_row__"]=df["Lead Source"].astype(str).apply(looks_internet)
    return df

# ---------- Session ----------
if "cost_inputs" not in st.session_state:
    st.session_state.cost_inputs = {
        "Dealer Website Leads": 1899,
        "Autoweb": 1200,
        "CarFax": 1000,
        "Cargurus": 899,
        "Cars.com": 0,
        "AutoTrader": 0,
        "GM Third Party": 3000,
        "Trade Pending": 900,
        "TrueCar": ("per_sale", 349),
        "Podium": 1500,
        "CarBravo DRP": 0,
        "Shop Click Drive": 0,
    }



# ---------- Sidebar ----------
st.sidebar.header("Data")
mode = st.sidebar.radio("Data mode", ["Single file", "Monthly files", "YTD comparison"], index=0)
# Store mode in session state for goal calculations
st.session_state["mode"] = mode
months_all = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
data_frames=[]

@st.dialog("Upload monthly files")
def mon_dialog(months):
    st.write("Upload one file per selected month:")
    uploaded=False
    for m in months:
        f=st.file_uploader(m, type=["xlsx"], key=f"dlg_{m}")
        if f:
            df = read_report(f); df["__dataset__"]="Combined"
            st.session_state.setdefault("monthly_frames", {})[m]=df; uploaded=True
    if st.button("Done"):
        if uploaded: st.rerun()
        else: st.warning("No files uploaded.")

if mode=="Single file":
    c1,c2=st.sidebar.columns(2, gap="small")
    with c1:
        f_new=st.file_uploader("Upload ROI file (New/Combined)", type=["xlsx"], key="single_new")
    with c2:
        compare_used=st.checkbox("Compare Used?", value=False)
    f_used=st.sidebar.file_uploader("Upload ROI file (Used)", type=["xlsx"], key="single_used") if compare_used else None
    start_m,end_m=st.sidebar.select_slider("Months in file (labels)", options=months_all, value=("Jan","Dec"))
    # Store in session state for goal calculations
    st.session_state["start_m"] = start_m
    st.session_state["end_m"] = end_m
    if f_new: 
        df_n=read_report(f_new); df_n["__dataset__"]="New/Combined"; data_frames.append(df_n)
    if f_used:
        df_u=read_report(f_used); df_u["__dataset__"]="Used"; data_frames.append(df_u)
elif mode=="Monthly files":
    sel=st.sidebar.multiselect("Months to include", months_all, default=["Jan","Feb","Mar"])
    # Store in session state for goal calculations
    st.session_state["sel"] = sel
    if st.sidebar.button("View / Upload"):
        if sel: mon_dialog(sel)
        else: st.sidebar.warning("Pick at least one month.")
    for m in sel:
        if "monthly_frames" in st.session_state and m in st.session_state.monthly_frames:
            data_frames.append(st.session_state.monthly_frames[m])
    start_m = sel[0] if sel else "Jan"; end_m = sel[-1] if sel else "Jan"
else:
    f_this=st.sidebar.file_uploader("This YTD", type=["xlsx"], key="ytd_this")
    f_last=st.sidebar.file_uploader("Last YTD", type=["xlsx"], key="ytd_last")
    start_m,end_m="Jan","Current"
    if f_this: d1=read_report(f_this); d1["__dataset__"]="This YTD"; data_frames.append(d1)
    if f_last: d2=read_report(f_last); d2["__dataset__"]="Last YTD"; data_frames.append(d2)

st.sidebar.header("Settings")
c1,c2=st.sidebar.columns(2)
with c1:
    pru_combined=st.number_input("PRU (New/Combined)", min_value=0, value=2153, step=50)
with c2:
    pru_used=st.number_input("PRU (Used, optional)", min_value=0, value=0, step=50)

exclude_weak=st.sidebar.checkbox('Exclude "* I Was Too Weak To Ask"', value=True)

st.sidebar.subheader("Costs")
for k in list(st.session_state.cost_inputs.keys()):
    v=st.session_state.cost_inputs[k]
    # Replace "Podium" with "Web Chat" in display only
    display_name = "Web Chat" if k == "Podium" else k
    if isinstance(v, tuple) and v[0]=="per_sale":
        st.session_state.cost_inputs[k]=("per_sale", st.sidebar.number_input(f"{display_name} — per sale", min_value=0, value=int(v[1]), step=10, key=f"c_{k}"))
    else:
        st.session_state.cost_inputs[k]=st.sidebar.number_input(f"{display_name} — monthly", min_value=0, value=int(v), step=50, key=f"c_{k}")

# ---------- Assemble ----------
if len(data_frames)==0:
    st.info("Upload at least one file to begin."); st.stop()

df_all=pd.concat(data_frames, ignore_index=True)

# Store original dataframe for filter tracking
df_original = df_all.copy()

# Define buckets that should be kept regardless of lead volume
WHITELIST_BUCKETS = {
    "Carguru", "Cars.com", "AutoTrader", "TrueCar", "CarFax", "Autoweb",
    "GM Third Party", "Trade In Leads", "Podium", "Web Chat", "CarBravo DRP",
    "Shop Click Drive", "Dealer Website Leads", "GMC.com", "GM Lease", "GM Loan/Payoff"
}

# Track low volume filtered sources
low_volume_sources = []
lead_source_groups = df_all.groupby("Lead Source")
for source, group in lead_source_groups:
    if (group["Total Leads"].sum() < 3 and 
        canonical_bucket(source) not in WHITELIST_BUCKETS):
        low_volume_sources.append({
            "Source": source,
            "Leads": group["Total Leads"].sum(),
            "Sales": group["Sold in Timeframe"].sum()
        })

# Apply lead volume filter (keep if >= 3 leads OR in whitelist)
df_all = df_all.groupby("Lead Source").filter(
    lambda x: (x["Total Leads"].sum() >= 3) or 
             (canonical_bucket(x["Lead Source"].iloc[0]) in WHITELIST_BUCKETS)
)

# Track credit sources before filtering
credit_sources = []
for source in df_all[df_all["Lead Source"].fillna("").str.contains("credit", case=False)]["Lead Source"].unique():
    group = df_all[df_all["Lead Source"] == source]
    credit_sources.append({
        "Source": source,
        "Leads": group["Total Leads"].sum(),
        "Sales": group["Sold in Timeframe"].sum()
    })

# Filter out any "Credit" sources entirely
df_all = df_all[~df_all["Lead Source"].fillna("").str.contains("credit", case=False, regex=False)]

# Add a small button in the corner to show filtered sources
col1, col2 = st.columns([0.9, 0.1])
with col2:
    with st.expander("📋 Filtered Sources", expanded=False):
        if len(credit_sources) > 0 or len(low_volume_sources) > 0:
            st.markdown("#### Filtered Out Sources")
            
            if len(credit_sources) > 0:
                st.markdown("##### Credit Applications")
                for src in credit_sources:
                    st.markdown(f"""
                    <div style='font-size:0.9em;padding:4px 0;'>
                        <div><b>{src['Source']}</b></div>
                        <div style='color:#9aa0a6;font-size:0.9em;'>
                            Leads: {num0(src['Leads'])} • Sales: {num0(src['Sales'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if len(low_volume_sources) > 0:
                st.markdown("##### Low Volume (< 3 leads)")
                for src in low_volume_sources:
                    st.markdown(f"""
                    <div style='font-size:0.9em;padding:4px 0;'>
                        <div><b>{src['Source']}</b></div>
                        <div style='color:#9aa0a6;font-size:0.9em;'>
                            Leads: {num0(src['Leads'])} • Sales: {num0(src['Sales'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("*No sources filtered*")

if exclude_weak:
    df_all=df_all[~df_all["Lead Source"].fillna("").str.contains("Weak To Ask", case=False, regex=False)]

def months_between(s, e):
    if s not in months_all or e not in months_all: return 1
    return (months_all.index(e)-months_all.index(s))+1
window_months = months_between(start_m, end_m)



def compute_cost(bucket: str, sold: int) -> float:
    """Compute cost for a bucket, handling Web Chat/Podium mapping."""
    ci = getattr(st.session_state, "cost_inputs", {})
    if not isinstance(ci, dict):
        return 0.0
    
    # Normalize bucket name
    key = canonical_bucket(bucket)
    
    # Special case: Web Chat inherits Podium cost
    if key == "Web Chat":
        monthly_cost = ci.get("Podium", 1500)  # Default to 1500 if not set
        return float(monthly_cost) * window_months
    
    # Get normalized cost inputs from cache or build cache
    cache_key = "__cost_by_bucket__"
    if cache_key not in st.session_state:
        norm = {}
        for k, v in ci.items():
            cb = canonical_bucket(k)
            norm[cb] = v
        st.session_state[cache_key] = norm
    by_bucket = st.session_state.get(cache_key, {})
    
    if key not in by_bucket:
        return 0.0
        
    v = by_bucket[key]
    if isinstance(v, tuple) and v[0] == "per_sale":
        return float(v[1]) * (sold or 0)
    
    return float(v) * window_months

def compute_agg(df):
    df=_ensure_bucket_col(df)
    df = _ensure_bucket_col(df)
    df = _ensure_bucket_col(df)
    df=_ensure_bucket_col(df)
    df=_ensure_bucket_col(df)
    df=_ensure_bucket_col(df)
    df=_ensure_bucket_col(df)
    agg=df.groupby(["Bucket"], dropna=False).agg(
        Leads=("Total Leads","sum"),
        Sold=("Sold in Timeframe","sum"),
        ApptsSet=("Appts Set","sum"),
        ApptsShown=("Appts Shown","sum"),
    ).reset_index()
    non_internet_keys = set([
        "Walk-In","Phone","Service","Service Dept","Body Shop","Parts","BDC Outbound","Referral","Repeat","Fleet","Event","Employee",
    ])
    agg["__internet__"] = agg["Bucket"].astype(str).apply(looks_internet)
    agg=agg[agg["Bucket"].str.upper()!="TOTAL"]
    has_used = "__dataset__" in df.columns and (df["__dataset__"]=="Used").any()
    use_pru = (pru_used if has_used and pru_used>0 else pru_combined)
    agg["PRU"]=use_pru
    agg["Profit"]=agg["Sold"]*agg["PRU"]
    agg["Cost"]=agg.apply(lambda r: compute_cost(r["Bucket"], r["Sold"]), axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        roix=np.where(agg["Cost"]>0, agg["Profit"]/agg["Cost"], agg["Sold"]*1.0)
    agg["ROIx"]=roix
    # mark paid channels on aggregate rows
    agg["__is_paid__"] = agg["Bucket"].astype(str).isin(PAID_BUCKETS)
    agg["LeadToSale%"]=np.where(agg["Leads"]>0, agg["Sold"]/agg["Leads"]*100.0, 0.0)
    agg["ApptSet%"]=np.where(agg["Leads"]>0, agg["ApptsSet"]/agg["Leads"]*100.0, 0.0)
    return agg


agg=compute_agg(df_all)


# ---------- Title & Inline Info ----------
title_col, info_col = st.columns([0.92, 0.08])
with title_col:
    st.markdown("# Lead ROI Bubble Map")
    st.caption("Build: v15ai • Internet toggle fixed + deltas aligned")
with info_col:
    with st.expander("ℹ️ Filters & Info"):
        # Rules & Grouping Info
        st.markdown("### Current Rules & Groupings")
        st.markdown("""
**Global Filters**
- Any source containing **"Credit"**
- Sources with **< 3 leads** (unless whitelisted)
- \*Optionally\*: `* I Was Too Weak To Ask` (when enabled)

**"Only Internet" excludes**
- **Service / Service Dept / GM Service**
- **Hill Car** (and related)
- **Repeat / Referral**
- **Drive By** variants
- Walk‑In/Showroom/Phone Up/Event/Parts

**Source Grouping**
- **TrueCar** → All variants ($349/sale)
- **Trade Pending** → Inc. TradePending
- **Dealer Website** → Inc. wallingfordgmc.com, Ansira
- **Podium/Web Chat** → $1,500/month
- **CarBravo/SCD** → CarBravo DRP, Shop Click Drive
""")
        
        # Show currently filtered sources
        if len(credit_sources) > 0 or len(low_volume_sources) > 0:
            st.markdown("### Currently Filtered Out")
            
            if len(credit_sources) > 0:
                with st.expander("Credit Applications", expanded=False):
                    for src in credit_sources:
                        st.markdown(f"""
                        <div style='font-size:0.9em;padding:4px 0;'>
                            <div><b>{src['Source']}</b></div>
                            <div style='color:#9aa0a6;font-size:0.9em;'>
                                Leads: {num0(src['Leads'])} • Sales: {num0(src['Sales'])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            if len(low_volume_sources) > 0:
                with st.expander("Low Volume Sources (< 3 leads)", expanded=False):
                    for src in low_volume_sources:
                        st.markdown(f"""
                        <div style='font-size:0.9em;padding:4px 0;'>
                            <div><b>{src['Source']}</b></div>
                            <div style='color:#9aa0a6;font-size:0.9em;'>
                                Leads: {num0(src['Leads'])} • Sales: {num0(src['Sales'])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
**Note on Paid Sources:**
A bucket is considered **Paid** when its cost > $0
(either monthly cost × window or per-sale cost × sales)
""")

# ---------- Title Hotlist ----------
internet_base = agg[agg["__internet__"]].copy()
bucket_count = internet_base.shape[0]
# ensure paid flag exists on internet_base
internet_base = _ensure_paid_flag(internet_base)
best_paid = internet_base[internet_base["__is_paid__"]].sort_values("ROIx", ascending=False).head(1)
best_appt_pct = internet_base.sort_values("ApptSet%", ascending=False).head(1)
top3_appt_pct = internet_base.sort_values('ApptSet%', ascending=False).head(3)

st.markdown(f"""
<div class="card" style="margin-top:-6px; margin-bottom:14px;">
  <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start;">
    <div><div class="subtle">Buckets (internet)</div><div style="font-weight:800">{bucket_count}</div></div>
    <div>
      <div class="subtle">Best Paid ROI</div>
      <div style="font-weight:700">{ (best_paid.iloc[0]['Bucket'] + ' — ' + roix_label(best_paid.iloc[0]['ROIx'])) if len(best_paid) else '—' }</div>
    </div>
    <div>
      <div class="subtle">Best Appt Set %</div>
      <div style="font-weight:700">{ (best_appt_pct.iloc[0]['Bucket'] + ' — ' + pct2(best_appt_pct.iloc[0]['ApptSet%'], cap_100=True)) if len(best_appt_pct) else '—' }</div>
    </div>
    <div>
      <div class="subtle">Top 3 by Appt Set %</div>
      <div style="font-weight:700">
        { "<br/>".join([f"• {r['Bucket']}: {pct2(r['ApptSet%'], cap_100=True)}" for _,r in top3_appt_pct.iterrows()]) }
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- Graph & Filters ----------
left,right=st.columns([3,1], gap="large")
with left:
    st.markdown("## Graph view")
    # Store internet toggle state in session state
    only_internet = st.toggle("Only Internet (vs All source types)", value=True)
    st.session_state["only_internet"] = only_internet
    paid_only = st.toggle("Paid sources only", value=True)  # Default to True
    
    base = agg[agg["__internet__"]] if only_internet else agg.copy()
    view = base if not paid_only else base[base["__is_paid__"]].copy()
    three_plus_sales = st.toggle("3 or more Sales", value=False)
    if three_plus_sales:
        view = view[view["Sold"] >= 3].copy()
    
    # Add Performance Warnings section with custom CSS
    st.markdown("""
    <style>
    .warning-container {
        max-height: 300px;
        overflow-y: auto;
        margin-bottom: 20px;
        padding: 10px;
        border: 1px solid rgba(231,76,60,0.2);
        border-radius: 10px;
        background: rgba(231,76,60,0.05);
    }
    .warning-card {
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        background: rgba(20,20,20,0.3);
        border: 1px solid rgba(231,76,60,0.2);
    }
    .warning-card.severe {
        border-left: 4px solid #e74c3c;
        background: rgba(231,76,60,0.15);
    }
    .warning-card.moderate {
        border-left: 4px solid #f39c12;
        background: rgba(243,156,18,0.1);
    }
    .warning-title {
        color: #e74c3c;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## Effectiveness Bubble Map")

    def roix_norm_static(x):
        import numpy as np
        if not np.isfinite(x): x=10.0
        x = max(0.0, min(float(x), 10.0))
        if x <= 3.0:
            return (x/3.0)*0.6
        elif x <= 5.0:
            return 0.6 + ((x-3.0)/2.0)*0.2
        else:
            return 0.8 + ((x-5.0)/5.0)*0.2

    plot = view.copy()

    # Calculate core metrics with caps at 100%
    plot["ContactRate"] = np.minimum(
        np.where(plot["Leads"] > 0, plot["ApptsSet"] / plot["Leads"] * 100.0, 0.0),
        100.0
    )
    plot["CloseRate"] = np.minimum(
        np.where(plot["Leads"] > 0, plot["Sold"] / plot["Leads"] * 100.0, 0.0),
        100.0
    )
    plot["CostPerSale"] = np.where(plot["Sold"] > 0, plot["Cost"] / plot["Sold"], 0.0)
    plot["size_val"] = plot["Leads"].apply(lambda v: np.log1p(v) * 2)  # Size based on lead volume
    plot["color_norm"] = plot["ROIx"].apply(roix_norm_static)  # ROI-based coloring
    
    # Enhanced hover text
    plot["hover"] = (
        "<b>" + plot["Bucket"].astype(str) + "</b><br>" +
        "<b>Contact Rate:</b> " + plot["ContactRate"].map(lambda x: pct2(x, cap_100=True)) + "<br>" +
        "<b>Close Rate:</b> " + plot["CloseRate"].map(lambda x: pct2(x, cap_100=True)) + "<br>" +
        "<b>ROI:</b> " + plot["ROIx"].map(roix_label) + "<br>" +
        "<b>Leads:</b> " + plot["Leads"].map(num0) + "<br>" +
        "<b>Sales:</b> " + plot["Sold"].map(num0) + "<br>" +
        "<b>Cost Per Sale:</b> " + plot["CostPerSale"].map(money0)
    )

    plot["label"] = plot["Bucket"]  # Show bucket names on bubbles

    colorscale=[(0.00,"#b22222"), (0.30,"#ff8c00"), (0.60,"#ffd700"), (0.80,"#1e90ff"), (1.00,"#0b3d91")]
    fixed_ticks=[0,3,5,10]
    tickvals=[roix_norm_static(t) for t in fixed_ticks]
    ticktext=["0x","3x","5x","10x+"]

    # Create scatter plot with new metrics
    fig = px.scatter(
        plot, x="CloseRate", y="ContactRate", 
        size="size_val", color="color_norm",
        text="label", custom_data=["hover", "Bucket"],
        labels={
            "CloseRate": "Close Rate (%)", 
            "ContactRate": "Contact Rate (%)"
        },
        color_continuous_scale=colorscale,
        range_color=(0.0, 1.0)
    )

    # Update marker styling
    fig.update_traces(
        marker=dict(opacity=0.92, line=dict(width=1, color="rgba(0,0,0,0.35)")),
        textposition="top center",
        hovertemplate="%{customdata[0]}<extra></extra>"
    )

    # Layout configuration
    fig.update_layout(
        title="Lead Source Performance Matrix",
        title_x=0.5,
        hoverlabel=dict(bgcolor="rgba(22,22,22,0.95)", font_size=13),
        height=760,
        coloraxis_colorbar=dict(
            title="ROI (x)", 
            tickvals=tickvals, 
            ticktext=ticktext
        ),
        plot_bgcolor="rgba(240,240,240,0.05)"
    )

    # Constants for quadrants
    CONTACT_GOAL = 50.0
    CPS_GOAL = 1000

    # Calculate the max close rate for dynamic x-axis (minimum 15%)
    max_close_rate = max(max(plot["CloseRate"]) * 1.1, 15)

    # Add green/red shading for contact rate goal
    fig.add_shape(
        type="rect", x0=0, x1=max_close_rate, y0=0, y1=50.0,
        fillcolor="rgba(231,76,60,0.05)", line_width=0,
        layer="below"
    )
    fig.add_shape(
        type="rect", x0=0, x1=max_close_rate, y0=50.0, y1=100,
        fillcolor="rgba(46,204,113,0.05)", line_width=0,
        layer="below"
    )

    # Add green/red shading for close rate goal
    fig.add_shape(
        type="rect", x0=0, x1=8.5, y0=0, y1=100,
        fillcolor="rgba(231,76,60,0.05)", line_width=0,
        layer="below"
    )
    fig.add_shape(
        type="rect", x0=8.5, x1=max_close_rate, y0=0, y1=100,
        fillcolor="rgba(46,204,113,0.05)", line_width=0,
        layer="below"
    )

    # Add goal lines with annotations
    fig.add_hline(
        y=50.0,  # Contact Rate goal
        line=dict(color="#27ae60", width=2, dash="dash"),
        annotation_text="Target Contact Rate (50%)",
        annotation_position="right"
    )
    fig.add_vline(
        x=8.5,  # Close Rate goal
        line=dict(color="#27ae60", width=2, dash="dash"),
        annotation_text="Target Close Rate (8.5%)",
        annotation_position="top"
    )

    # Update axes with better formatting
    fig.update_xaxes(
        title_text="Close Rate (%)",
        range=[0, max_close_rate],  # Dynamic max close rate
        tickformat=".1f",
        gridcolor="rgba(128,128,128,0.1)",
        zerolinecolor="rgba(128,128,128,0.2)"
    )
    fig.update_yaxes(
        title_text="Contact Rate (%)",
        range=[0, 100],  # Fixed range for contact rate
        tickformat=".0f",
        gridcolor="rgba(128,128,128,0.1)",
        zerolinecolor="rgba(128,128,128,0.2)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Totals
    st.markdown("#### Totals for this view")
    leads= view["Leads"].sum(); sold=view["Sold"].sum()
    profit=view["Profit"].sum(); cost=view["Cost"].sum()
    roix_total=(profit/cost) if cost>0 else float(sold) if sold>0 else 0.0
    soldpct=(sold/leads*100.0) if leads>0 else 0.0
    # --- Goals + deltas for Totals ---
    g = st.session_state.get("__goals__", {"units_total_goal":567,"internet_ratio_goal":0.85,"sold_rate_goal":8.5,"contact_rate_goal":50.0})
    only_internet = st.session_state.get("only_internet", False)
    goal_units_effective = int(st.session_state.get("__dynamic_units_goal__", 0)) or _dynamic_units_goal()[0]
    st.session_state["__dynamic_units_goal__"] = goal_units_effective
    _pru = locals().get("pru_combined", (profit/sold if sold>0 else 0))
    goal_profit = goal_units_effective * (locals().get("pru_combined", (profit/sold if sold>0 else 0)))
    units_delta_pct   = ((sold - goal_units_effective) / goal_units_effective * 100.0) if goal_units_effective>0 else 0.0
    soldrate_delta_pp = soldpct - float(g["sold_rate_goal"])
    profit_delta_pct  = ((profit - goal_profit) / goal_profit * 100.0) if goal_profit>0 else 0.0
    # -- dynamic goal guard (robust only_internet key) --
    only_internet = bool(st.session_state.get("only_internet", st.session_state.get("Only Internet", st.session_state.get("Only_Internet", st.session_state.get("onlyInternet", False)))))
    if "__dynamic_units_goal__" not in st.session_state:
        base = locals().get("goal_units_total", int(st.session_state.get("__goals__", {}).get("units_total_goal", 567)))
        st.session_state["__dynamic_units_goal__"] = int(round(base * (0.85 if only_internet else 1.0)))
    goal_units_effective = int(st.session_state["__dynamic_units_goal__"])
    # Calculate new metrics
    cost_per_sale = cost/sold if sold > 0 else 0
    cost_per_lead = cost/leads if leads > 0 else 0
    contact_rate = view["ApptsSet"].sum()/leads*100.0 if leads > 0 else 0
    
    a,b,c,d,e,f = st.columns(6)
    a.metric("Leads", num0(leads))
    b.metric("Sold (units)", num0(sold))
    c.metric("Cost Per Sale", money0(cost_per_sale))
    d.metric("Cost Per Lead", money0(cost_per_lead))
    e.metric("Contact Rate", pct2(contact_rate, cap_100=True))
    f.metric("ROI", roix_label(roix_total))
    # ---- Goals for this view ----
    g = st.session_state.get("__goals__", {
        "sold_rate_goal": 8.5,
        "contact_rate_goal": 50.0
    })
    
    # Get effective and base goals using dynamic calculation
    goal_units_effective, goal_units_base, is_internet = _dynamic_units_goal()
    
    # Calculate goal metrics
    goal_profit = goal_units_effective * (locals().get("pru_combined", (profit/sold if sold>0 else 0)))
    contact_rate_actual = (view["ApptsSet"].sum()/view["Leads"].sum()*100.0) if view["Leads"].sum()>0 else 0.0
    sold_pct_actual = (sold/leads*100.0) if leads>0 else 0.0
    
    # Check if goals are met
    sold_ok = sold >= goal_units_effective
    sold_rate_ok = sold_pct_actual >= g["sold_rate_goal"]
    contact_ok = contact_rate_actual >= g["contact_rate_goal"]
    
    # Set colors based on performance
    units_color = "#2ecc71" if sold_ok else "#e74c3c"
    soldrate_color = "#2ecc71" if sold_rate_ok else "#e74c3c"
    contact_color = "#2ecc71" if contact_ok else "#e74c3c"
    st.markdown(f"""
    <div class="card" style="margin-top:8px; padding:10px 12px; border-radius:12px; background:rgba(0,0,0,0.04)">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px">
        <div style="font-weight:800">Goals for this view</div>
        <div><span class="badge">{'Internet scope' if only_internet else 'All sources'}</span></div>
      </div>
      <div style="display:flex; gap:24px; flex-wrap:wrap">
        <div><div class="subtle">Units Goal {' (with 85% Internet)' if only_internet else ''}</div><div style="font-weight:700; color:{units_color}">{num0(goal_units_effective)}<div class="subtle" style="font-weight:400">({num0(goal_units_base)} base)</div></div></div>
        <div><div class="subtle">Sold (Actual)</div><div style="font-weight:700">{num0(sold)}</div></div>
        <div><div class="subtle">Lead → Sale % Goal</div><div style="font-weight:700; color:{soldrate_color}">{pct2(g['sold_rate_goal'])}</div></div>
        <div><div class="subtle">Contact Rate % Goal</div><div style="font-weight:700; color:{contact_color}">{pct2(g['contact_rate_goal'])}</div></div>
        <div><div class="subtle">Profit Goal (PRU × Units)</div><div style="font-weight:700">{money0(goal_profit)}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Edit YTD Goals"):
        st.session_state["show_goals_editor"] = True
        st.rerun()



with right:
    st.markdown("## Top 10")
    how = "Only Internet" if True else "All source types"  # label display only
    st.caption("Top performers by ROI — {}".format(how))
    hide_unpaid_extra = st.toggle("Hide Un-Paid sources", value=False, key="hide_unpaid_extra")

    # Build base then apply extra filter
    base_view = agg[agg["__internet__"]]  # Top10 aligns with internet scope in this panel
    top_source = base_view.copy()
    if hide_unpaid_extra:
        top_source = top_source[top_source["Cost"]>0]
        if len(top_source)<10:
            filler = base_view[base_view["Cost"]>0].sort_values("ROIx", ascending=False)
            exist=set(top_source["Bucket"])
            for _,row in filler.iterrows():
                if row["Bucket"] not in exist:
                    top_source = pd.concat([top_source, row.to_frame().T], ignore_index=True)
                if len(top_source)>=10: break
    top= top_source.sort_values("ROIx", ascending=False).head(10)

    if len(top):
        cards_html = ""
        for _, r in top.iterrows():
            is_unpaid = (r['Cost'] <= 0)
            gray = "opacity:.55;filter:grayscale(50%);" if is_unpaid else ""
            badge = '<span class="badge">No cost</span>' if is_unpaid else ""
            cards_html += f"""
<div class=\"card\" style=\"{gray}\">
  <div style=\"font-weight:800;margin-bottom:4px\">{r['Bucket']}{badge}</div>
  <div>ROI: <b>{roix_label(r['ROIx'])}</b></div>
  <div>Profit: {money0(r['Profit'])} - Cost: {money0(r['Cost'])}</div>
  <div>Sold: {num0(r['Sold'])} - Leads: {num0(r['Leads'])}</div>
  <div>Lead→Sale: {pct2((r['Sold']/r['Leads']*100.0) if r['Leads']>0 else 0, cap_100=True)} - Contacts: {num0(r['ApptsSet'])}</div>
</div>
"""
        st.markdown(f'<div style="height:820px;overflow-y:auto;padding-right:8px">{cards_html}</div>', unsafe_allow_html=True)
        st.caption("Note: grayed cards are unpaid (Cost = $0).")
    else:
        st.info("No sources to display.")

# ---------- Opportunities ----------
st.markdown("---")
st.markdown("## Improvement Opportunities")

# Add custom CSS for the opportunities section
st.markdown("""
<style>
.opportunities-container {
    display: flex;
    gap: 24px;
    margin-bottom: 20px;
    align-items: stretch;
}
.opportunities-column {
    flex: 1;
    background: rgba(20,20,20,0.2);
    border-radius: 10px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    min-width: 0;  /* Prevent flex items from overflowing */
}
.opportunity-card {
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    border: 1px solid rgba(231,76,60,0.2);
    flex-shrink: 0;  /* Prevent cards from shrinking */
    height: 85px;  /* Fixed height for cards */
}
.opportunity-list {
    height: 380px;  /* Fixed height for 4 cards + margins */
    overflow-y: auto;
    padding-right: 8px;
    margin-top: 8px;
}
.opportunity-header {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
}
.severity-high {
    background: rgba(231,76,60,0.15);
    border-left: 4px solid #e74c3c;
}
.severity-medium {
    background: rgba(241,196,15,0.1);
    border-left: 4px solid #f1c40f;
}
.severity-low {
    background: rgba(243,156,18,0.1);
    border-left: 4px solid #f39c12;
}
</style>
""", unsafe_allow_html=True)

# Calculate opportunities
low_contact = view[view["ApptsSet"] > 0].copy()
low_contact["ContactRate"] = (low_contact["ApptsSet"] / low_contact["Leads"] * 100.0)
low_contact = low_contact[low_contact["ContactRate"] < 50].sort_values("ContactRate")

high_cps = view[view["Sold"] > 0].copy()
high_cps["CostPerSale"] = high_cps["Cost"] / high_cps["Sold"]
high_cps = high_cps[high_cps["CostPerSale"] > 1000].sort_values("CostPerSale", ascending=False)

# Create two-column layout
st.markdown("""
<div class="opportunities-container">
    <div class="opportunities-column">
        <div class="opportunity-header">🔴 Low Contact Rate Sources</div>
        <div class="opportunity-list">
""", unsafe_allow_html=True)

# Low Contact Rate column
for _, row in low_contact.head(8).iterrows():
    contact_rate = (row["ApptsSet"] / row["Leads"] * 100.0) if row["Leads"] > 0 else 0
    severity = "high" if contact_rate < 20 else ("medium" if contact_rate < 35 else "low")
    st.markdown(f"""
        <div class="opportunity-card severity-{severity}">
            <div style="font-weight:600">{row["Bucket"]}</div>
            <div>Contact Rate: <b>{pct2(contact_rate, cap_100=True)}</b></div>
            <div style="color:#9aa0a6;font-size:0.9em">
                Leads: {num0(row["Leads"])} • 
                Contacts: {num0(row["ApptsSet"])}
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
        </div>
    </div>
    <div class="opportunities-column">
        <div class="opportunity-header">💰 High Cost Per Sale</div>
        <div class="opportunity-list">
""", unsafe_allow_html=True)

# High Cost Per Sale column
for _, row in high_cps.head(8).iterrows():
    cps = row["Cost"] / row["Sold"] if row["Sold"] > 0 else 0
    severity = "high" if cps > 2000 else ("medium" if cps > 1500 else "low")
    st.markdown(f"""
        <div class="opportunity-card severity-{severity}">
            <div style="font-weight:600">{row["Bucket"]}</div>
            <div>Cost Per Sale: <b>{money0(cps)}</b></div>
            <div style="color:#9aa0a6;font-size:0.9em">
                Sales: {num0(row["Sold"])} • 
                Total Cost: {money0(row["Cost"])}
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Opportunities ----------
st.markdown("---")
st.markdown("## Improvement Opportunities")

# Add custom CSS for the opportunities section
st.markdown("""
<style>
.opportunities-wrapper {
    background: rgba(20,20,20,0.2);
    border-radius: 10px;
    padding: 16px;
    margin: 16px 0;
}
.opportunities-container {
    display: flex;
    gap: 24px;
}
.opportunities-column {
    flex: 1;
    min-width: 0;
}
.opportunity-card {
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    border: 1px solid rgba(231,76,60,0.2);
    height: 85px;
}
.opportunity-list {
    height: 360px;
    overflow-y: auto;
    padding-right: 8px;
}
.opportunity-header {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    color: #ffffff;
}
.severity-high {
    background: rgba(231,76,60,0.15);
    border-left: 4px solid #e74c3c;
}
.severity-medium {
    background: rgba(241,196,15,0.1);
    border-left: 4px solid #f1c40f;
}
.severity-low {
    background: rgba(243,156,18,0.1);
    border-left: 4px solid #f39c12;
}
</style>
""", unsafe_allow_html=True)

# Calculate opportunities
low_contact = view[view["ApptsSet"] > 0].copy()
low_contact["ContactRate"] = (low_contact["ApptsSet"] / low_contact["Leads"] * 100.0)
low_contact = low_contact[low_contact["ContactRate"] < 50].sort_values("ContactRate")

high_cps = view[view["Sold"] > 0].copy()
high_cps["CostPerSale"] = high_cps["Cost"] / high_cps["Sold"]
high_cps = high_cps[high_cps["CostPerSale"] > 1000].sort_values("CostPerSale", ascending=False)

# Create contained two-column layout
st.markdown("""
<div class="opportunities-wrapper">
    <div class="opportunities-container">
        <div class="opportunities-column">
            <div class="opportunity-header">🔴 Low Contact Rate Sources</div>
            <div class="opportunity-list">
""", unsafe_allow_html=True)

# Low Contact Rate column
for _, row in low_contact.head(8).iterrows():
    contact_rate = (row["ApptsSet"] / row["Leads"] * 100.0) if row["Leads"] > 0 else 0
    severity = "high" if contact_rate < 20 else ("medium" if contact_rate < 35 else "low")
    st.markdown(f"""
        <div class="opportunity-card severity-{severity}">
            <div style="font-weight:600">{row["Bucket"]}</div>
            <div>Contact Rate: <b>{pct2(contact_rate, cap_100=True)}</b></div>
            <div style="color:#9aa0a6;font-size:0.9em">
                Leads: {num0(row["Leads"])} • 
                Contacts: {num0(row["ApptsSet"])}
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
            </div>
        </div>
        <div class="opportunities-column">
            <div class="opportunity-header">💰 High Cost Per Sale</div>
            <div class="opportunity-list">
""", unsafe_allow_html=True)

# High Cost Per Sale column
for _, row in high_cps.head(8).iterrows():
    cps = row["Cost"] / row["Sold"] if row["Sold"] > 0 else 0
    severity = "high" if cps > 2000 else ("medium" if cps > 1500 else "low")
    st.markdown(f"""
        <div class="opportunity-card severity-{severity}">
            <div style="font-weight:600">{row["Bucket"]}</div>
            <div>Cost Per Sale: <b>{money0(cps)}</b></div>
            <div style="color:#9aa0a6;font-size:0.9em">
                Sales: {num0(row["Sold"])} • 
                Total Cost: {money0(row["Cost"])}
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Opportunities ----------
st.markdown("---")
st.markdown("## Improvement Opportunities")

# Calculate opportunities
low_contact = view[view["ApptsSet"] > 0].copy()
low_contact["ContactRate"] = (low_contact["ApptsSet"] / low_contact["Leads"] * 100.0)
low_contact = low_contact[low_contact["ContactRate"] < 50].sort_values("ContactRate")

high_cps = view[view["Sold"] > 0].copy()
high_cps["CostPerSale"] = high_cps["Cost"] / high_cps["Sold"]
high_cps = high_cps[high_cps["CostPerSale"] > 1000].sort_values("CostPerSale", ascending=False)

# Single container for opportunities
st.markdown("""
<style>
.opps-container {
    background: rgba(20,20,20,0.2);
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
}
.opps-columns {
    display: flex;
    gap: 20px;
}
.opps-column {
    flex: 1;
}
.opps-header {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    color: #ffffff;
}
.opps-list {
    height: 340px;
    overflow-y: auto;
    padding-right: 8px;
}
.opp-card {
    background: rgba(0,0,0,0.2);
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
}
.severity-high { border-left: 4px solid #e74c3c; background: rgba(231,76,60,0.15); }
.severity-medium { border-left: 4px solid #f1c40f; background: rgba(241,196,15,0.1); }
.severity-low { border-left: 4px solid #f39c12; background: rgba(243,156,18,0.1); }
</style>

<div class="opps-container">
    <div class="opps-columns">
        <div class="opps-column">
            <div class="opps-header">🔴 Low Contact Rate Sources</div>
            <div class="opps-list">
""", unsafe_allow_html=True)

# Low Contact Rate column
for _, row in low_contact.head(8).iterrows():
    contact_rate = (row["ApptsSet"] / row["Leads"] * 100.0) if row["Leads"] > 0 else 0
    severity = "high" if contact_rate < 20 else ("medium" if contact_rate < 35 else "low")
    st.markdown(f"""
        <div class="opp-card severity-{severity}">
            <div style="font-weight:600">{row["Bucket"]}</div>
            <div>Contact Rate: <b>{pct2(contact_rate, cap_100=True)}</b></div>
            <div style="color:#9aa0a6;font-size:0.9em">
                Leads: {num0(row["Leads"])} • 
                Contacts: {num0(row["ApptsSet"])}
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
            </div>
        </div>
        <div class="opps-column">
            <div class="opps-header">💰 High Cost Per Sale</div>
            <div class="opps-list">
""", unsafe_allow_html=True)

# High Cost Per Sale column
for _, row in high_cps.head(8).iterrows():
    cps = row["Cost"] / row["Sold"] if row["Sold"] > 0 else 0
    severity = "high" if cps > 2000 else ("medium" if cps > 1500 else "low")
    st.markdown(f"""
        <div class="opp-card severity-{severity}">
            <div style="font-weight:600">{row["Bucket"]}</div>
            <div>Cost Per Sale: <b>{money0(cps)}</b></div>
            <div style="color:#9aa0a6;font-size:0.9em">
                Sales: {num0(row["Sold"])} • 
                Total Cost: {money0(row["Cost"])}
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Details ----------
st.markdown("---")
st.markdown("## Details")
# Build Details options: buckets + pass-through raw sources (robust + case-insensitive)
possible_lead_cols = ["Lead Source","LeadSource","source","Source","Lead_Source","__source__","__lead_source__","Lead source"]
lead_col = next((c for c in possible_lead_cols if c in base.columns), None)
raw_sources = base[lead_col].fillna("").astype(str) if lead_col else pd.Series([], dtype=str)
buckets = agg["Bucket"].astype(str)
combined = pd.concat([buckets, raw_sources], ignore_index=True)
norm = combined.str.strip().str.lower()
mask = ~norm.duplicated(keep="first")
options = sorted(pd.unique(base["Bucket"].astype(str)))

bucket_opts = options
if bucket_opts:
    selected_bucket = st.selectbox("Select a bubble to inspect:", bucket_opts, index=0)
    sel=agg[agg["Bucket"]==selected_bucket].iloc[0]
    net=sel["Profit"]-sel["Cost"]
    sold_pct = (sel["Sold"]/sel["Leads"]*100.0) if sel["Leads"]>0 else 0.0
    set_pct  = (sel["ApptsSet"]/sel["Leads"]*100.0) if sel["Leads"]>0 else 0.0
    shown_pct= (sel["ApptsShown"]/sel["ApptsSet"]*100.0) if sel["ApptsSet"]>0 else 0.0
    sold_of_appt = (sel["Sold"]/sel["ApptsShown"]*100.0) if sel["ApptsShown"]>0 else 0.0

    sold_color = "#f1c40f" if 1<=sold_pct<=6 else ("#2ecc71" if 7<=sold_pct<=10 else ("#5dade2" if sold_pct>10 else "#c0392b"))
    shown_color = "#f1c40f" if shown_pct<45 else "#2ecc71"
    sold_appt_color = "#f1c40f" if sold_of_appt<42 else "#2ecc71"

    st.markdown(f"""
<div class="card">
  <div style="font-size:20px;font-weight:800;margin-bottom:6px">{selected_bucket}</div>
  <div class="subtle" style="margin-bottom:12px">Source overview</div>
  <div style="display:flex;gap:32px;flex-wrap:wrap">
    <div><div class="subtle">Sold %</div><div style="font-weight:700;color:{sold_color}">{pct2(sold_pct, cap_100=True)}</div></div>
    <div><div class="subtle">ROI</div><div style="font-weight:700">{roix_label(sel['ROIx'])}</div></div>
    <div><div class="subtle">PRU</div><div style="font-weight:700">{money0(sel['PRU'])}</div></div>
    <div><div class="subtle">Leads</div><div style="font-weight:700">{num0(sel['Leads'])}</div></div>
    <div><div class="subtle">Sold (units)</div><div style="font-weight:700">{num0(sel['Sold'])}</div></div>
    <div><div class="subtle">Contacts (Appts Set)</div><div style="font-weight:700">{num0(sel['ApptsSet'])} <span class="subtle">({pct2(set_pct, cap_100=True)})</span></div></div>
    <div><div class="subtle">Appts Shown</div><div style="font-weight:700">{num0(sel['ApptsShown'])} <span style="color:{shown_color}">({pct2(shown_pct, cap_100=True)})</span></div></div>
    <div><div class="subtle">Sold % of Appt</div><div style="font-weight:700;color:{sold_appt_color}">{pct2(sold_of_appt, cap_100=True)}</div></div>
  </div>
  <hr style="border-color:rgba(255,255,255,.08)"/>
  <div style="display:flex;gap:24px;flex-wrap:wrap">
    <div><div class="subtle">Revenue (PRU × Sold)</div><div style="font-weight:700">{money0(sel['Profit'])}</div></div>
    <div><div class="subtle">Cost</div><div style="font-weight:700">{money0(sel['Cost'])}</div></div>
    <div><div class="subtle">Net Profit</div><div style="font-weight:700">{money0(net)}</div></div>
  </div>
  <div class="subtle" style="margin-top:8px;font-size:13px">Calc: Net = (PRU × Sold) − Cost → {money0(sel['PRU'])} × {num0(sel['Sold'])} − {money0(sel['Cost'])} = {money0(net)}</div>
</div>
""", unsafe_allow_html=True)
# ================== v15aj overrides appended ==================
# Lead Source → Bucket overrides (CSV) + expanded mapping

import csv, os, re as _re_patch

def _v15aj_normalize(s: str) -> str:
    return _re_patch.sub(r"\s+", " ", (s or "").strip().lower())

def _v15aj_load_overrides(path: str = "unmapped_lead_sources.csv"):
    try:
        if not os.path.exists(path):
            return {}
        overrides = {}
        with open(path, "r", encoding="utf-8-sig") as f:
            rdr = csv.DictReader(f)
            for row in rdr:
                src = (row.get("Lead Source") or "").strip()
                bkt = (row.get("Bucket") or "").strip()
                if not src:
                    continue
                overrides[_v15aj_normalize(src)] = bkt
        return overrides
    except Exception:
        return {}

if "__bucket_overrides__" not in st.session_state:
    st.session_state["__bucket_overrides__"] = _v15aj_load_overrides()

# Re-define canonical_bucket to take precedence over earlier version
def canonical_bucket(name: str) -> str:
    nraw = (name or "").strip()
    n = _v15aj_normalize(nraw)

    # 1) CSV overrides
    ov = st.session_state.get("__bucket_overrides__", {})
    if n in ov:
        chosen = (ov[n] or "").strip()
        if chosen.lower() == "unmapped":
            return nraw  # pass-through as its own source
        return chosen

    # 2) Rule-based mapping (expanded)
    # Carguru / Cargurus / guru => unified "Carguru"
    if ("guru" in n):
        return "Carguru"
# Dealer website-ish
    if ("dealer website" in n) or ("gm dealer website" in n) or ("wallingfordgmc.com" in n) or ("wallingfordbuickgmc.com" in n) or ("wearebuickgmc.com" in n):
        return "Dealer Website Leads"

    # Major marketplaces
    if "autotrader" in n or "auto trader" in n:
        return "AutoTrader"
    if "cars.com" in n or "carscom" in n:
        return "Cars.com"
    if "truecar" in n or "true car" in n:
        return "TrueCar"
    if "carfax" in n:
        return "CarFax"
    if "autoweb" in n:
        return "Autoweb"
    if "trade pending" in n or "tradepending" in n:
        return "Trade Pending"
    if "gm 3rd party" in n or "gm third party" in n or "gm 3rd" in n:
        return "GM Third Party"
    if "shop click drive" in n or n.startswith("scd"):
        return "Shop Click Drive"
    if n.startswith("carbravo drp") or "carbravo" in n:
        return "CarBravo DRP"

    # Credit Applications (expanded to include finance-related terms)
    if ("credit" in n) or ("prequal" in n) or ("pre-qual" in n) or ("prequalify" in n) or ("pre qualification" in n) or ("finance" in n):
        return "Credit Application"

    # Podium
    if "podium" in n:
        return "Podium"

    # 3) Fallback: pass-through
    return nraw
# ================== /v15aj overrides ==================


def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns:
            return c
    return None


def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns:
            return c
    return None




def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns: return c
    return None

def _ensure_bucket_col(df):
    lead_col = _guess_lead_col(df)
    if lead_col is None:
        if "Bucket" not in df.columns:
            df["Bucket"]="Unknown"
        return df
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # Reinforce Dealer Website Leads
    df.loc[s.str.contains("amp") | s.str.contains("hand-raiser web") | s.str.contains("interactivetel") | s.str.contains("wallingford buick gmc - interactivetel") | s.str.contains("do -") | s.str.contains("di -") | s.str.contains("ansira") | s.str.contains("wallingfordbuickgmc.com"), "Bucket"] = "Dealer Website Leads"

    # Web Chat (includes Podium)
    df.loc[s.str.contains("web chat") | s.str.contains("podium"), "Bucket"] = "Web Chat"

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (s.str.contains("gmc") & (s.str.contains("offer raq") | s.str.contains("build your own") | s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") | s.str.contains("supplier discount")))
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Carguru rollup
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"
    return df


    # Canonical map (CSV first, then rules)
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)

    # Hard re-enforcement for families that often slip (vectorized masks)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (
        s.str.contains("gmc") & (
            s.str.contains("offer raq") | s.str.contains("build your own") |
            s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") |
            s.str.contains("supplier discount")
        )
    )
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # Dealer Website Leads wide mask
    df.loc[s.str.contains("do -") | s.str.contains("di -") | s.str.contains("ansira") | s.str.contains("wallingfordbuickgmc.com"), "Bucket"] = "Dealer Website Leads"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Dealer Website Leads additions
    df.loc[s.str.contains("hand-raiser web") | s.str.contains("interactivetel"), "Bucket"] = "Dealer Website Leads"

    # Social Media
    df.loc[s.str.contains("youtube"), "Bucket"] = "Social Media"

    # Carguru roll-up (safety)
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"

    return df


    # Canonical map
    df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)
    s = df[lead_col].astype(str).str.lower().fillna("")

    # GMC.com family
    gmc_mask = (s.str.contains("gmc.com")) | (
        s.str.contains("gmc") & (
            s.str.contains("offer raq") | s.str.contains("build your own") |
            s.str.contains("locate vehicle") | s.str.contains("locate a vehicle") |
            s.str.contains("supplier discount")
        )
    )
    df.loc[gmc_mask, "Bucket"] = "GMC.com"

    # GM split (strict)
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Dealer Website Leads additions
    df.loc[s.str.contains("hand-raiser web") | s.str.contains("interactivetel"), "Bucket"] = "Dealer Website Leads"

    # Social Media
    df.loc[s.str.contains("youtube"), "Bucket"] = "Social Media"

    # Carguru roll-up (safety)
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"

    return df


def _normalize_cost_inputs(cost_inputs: dict, canonical=canonical_bucket, paid_buckets=None):
    paid = set(paid_buckets or PAID_BUCKETS)
    out = {}
    for k,v in (cost_inputs or {}).items():
        b = canonical(k)
        out[b] = out.get(b, 0) + float(v or 0)
    # zero-out costs for non-paid buckets (e.g., GMC.com shouldn't have cost)
    return {b:(val if b in paid else 0.0) for b,val in out.items()}
