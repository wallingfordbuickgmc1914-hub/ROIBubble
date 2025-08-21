
import streamlit as st


import re as _re

def _norm_key(s: str) -> str:
    return _re.sub(r"\s+", " ", (s or "").strip().lower())

def canonical_bucket(name: str) -> str:
    nraw = (name or "").strip()
    n = _norm_key(nraw)

    # CSV overrides first
    try:
        ov = st.session_state.get("__bucket_overrides__", {})
    except Exception:
        ov = {}
    if n in ov:
        b = (ov[n] or "").strip()
        return nraw if b.lower()=="unmapped" else b

    # ---- Consolidations / rollups ----
    # Website Chat (Web Chat + Podium grouped together)
    if ("web chat" in n) or ("podium" in n):
        return "Website Chat"

    # Dealer Website Leads (broad rules + prior ones)
    if ("amp" in n or "hand-raiser web" in n or "interactivetel" in n
        or "wallingford buick gmc - interactivetel" in n
        or "do -" in n or "di -" in n or "ansira" in n or "wallingfordbuickgmc.com" in n):
        return "Dealer Website Leads"

    # Social Media
    if "youtube" in n:
        return "Social Media"

    # GMC.com family
    if ("gmc.com" in n) or ("gmc" in n and (
        "offer raq" in n or "build your own" in n or "locate vehicle" in n or "locate a vehicle" in n or "supplier discount" in n
    )):
        return "GMC.com"

    # GM split (strict)
    if (("gm" in n) or ("gm financial" in n)) and ("lease" in n):
        return "GM Lease"
    if (("gm" in n) or ("gm financial" in n)) and (("loan" in n) or ("payoff" in n) or ("pay off" in n)):
        return "GM Loan/Payoff"

    # Trade-in ecosystems
    if ("kbb" in n) or ("kelley blue book" in n) or ("instant cash offer" in n) or ("ico" in n) \
       or ("trade pending" in n) or ("tradepending" in n) or ("trade-pending" in n):
        return "Trade In Leads"

    # Marketplaces & others
    if "guru" in n:
        return "Carguru"
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

    return nraw


    plot["label"]=plot["ROIx"].apply(roix_label)

    colorscale=[(0.00,"#b22222"), (0.30,"#ff8c00"), (0.60,"#ffd700"), (0.80,"#1e90ff"), (1.00,"#0b3d91")]
    fixed_ticks=[0,3,5,10]
    tickvals=[roix_norm_static(t) for t in fixed_ticks]
    ticktext=["0x","3x","5x","10x+"]

    fig=px.scatter(
        plot, x="LeadToSale%", y="ApptSet%", size="size_val", color="color_norm",
        text="label", custom_data=["hover","Bucket"],
        labels={"LeadToSale%":"Lead → Sale %", "ApptSet%":"Contact Rate (%)"},
        color_continuous_scale=colorscale, range_color=(0.0,1.0)
    )
    fig.update_traces(marker=dict(opacity=0.92, line=dict(width=1, color="rgba(0,0,0,0.35)")),
                      textposition="top center",
                      hovertemplate="%{customdata[0]}<extra></extra>")
    fig.update_layout(hoverlabel=dict(bgcolor="rgba(22,22,22,0.95)", font_size=13),
                      height=760,
                      coloraxis_colorbar=dict(title="ROI (x)", tickvals=tickvals, ticktext=ticktext))

    # Goal overlays
    CONTACT_GOAL = 50.0
    SOLD_PCT_GOAL = 8.5
    fig.add_hrect(y0=CONTACT_GOAL, y1=100, fillcolor="rgba(46,204,113,0.10)", line_width=0)
    fig.add_hrect(y0=0, y1=CONTACT_GOAL, fillcolor="rgba(231,76,60,0.08)", line_width=0)
    fig.add_vrect(x0=SOLD_PCT_GOAL, x1=100, fillcolor="rgba(46,204,113,0.08)", line_width=0)
    fig.add_vrect(x0=0, x1=SOLD_PCT_GOAL, fillcolor="rgba(231,76,60,0.06)", line_width=0)
    fig.add_hline(y=CONTACT_GOAL, line=dict(color="#27ae60", width=2, dash="dash"))
    fig.add_vline(x=SOLD_PCT_GOAL, line=dict(color="#27ae60", width=2, dash="dash"))

    fig.update_yaxes(title_text="Contact Rate (%)", range=[0,100])
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
    a,b,c,d,e,f=st.columns(6)
    a.metric("Leads", num0(leads))
    b.metric("Sold (units)", num0(sold), delta=f"{units_delta_pct:+.1f}%")
    c.metric("Sold %", pct2(soldpct, cap_100=True), delta=f"{soldrate_delta_pp:+.1f}pp")
    d.metric("Profit", money0(profit), delta=f"{profit_delta_pct:+.1f}%")
    e.metric("Cost", money0(cost))
    f.metric("ROI", roix_label(roix_total))
    # ---- Goals for this view ----
    g = st.session_state.get("__goals__", {"units_total_goal":567, "internet_ratio_goal": 0.85, "sold_rate_goal":8.5, "contact_rate_goal":50.0})
    
    # Compute units goal based on month scope
    try:
        mode  # see if variable exists
    except NameError:
        mode = "Single file"
    # Try to detect selected months from existing controls
    start_month = locals().get("start_m", "Jan")
    end_month   = locals().get("end_m", "Dec")
    selected_months = locals().get("sel", None)
    goal_units_total = units_goal_for_scope(mode, start_month, end_month, selected_months)
    goal_units_effective, goal_units_base, only_internet = _dynamic_units_goal()
    goal_profit = goal_units_effective * (locals().get("pru_combined", (profit/sold if sold>0 else 0)))
    contact_rate_actual = (view["ApptsSet"].sum()/view["Leads"].sum()*100.0) if view["Leads"].sum()>0 else 0.0
    sold_pct_actual = (sold/leads*100.0) if leads>0 else 0.0
    sold_ok = sold >= goal_units_effective
    sold_rate_ok = sold_pct_actual >= g["sold_rate_goal"]
    contact_ok = contact_rate_actual >= g["contact_rate_goal"]
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
        <div><div class="subtle">Units Goal</div><div style="font-weight:700; color:{units_color}">{num0(goal_units_effective)}<div class="subtle" style="font-weight:400">({num0(goal_units_total)} base)</div></div></div>
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
    base_view = agg[agg["__internet__"] = agg["Bucket"].astype(str).apply(looks_internet)
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
        return "Website Chat"

    # 3) Fallback: pass-through
    return nraw
# ================== /v15aj overrides ==================


def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns: return c
    return None


def _guess_lead_col(df):
    for c in ["Lead Source","LeadSource","Source","source","Lead_Source","Lead source","__source__","__lead_source__"]:
        if c in df.columns: return c
    return None

def _ensure_bucket_col(df):
    lead = _guess_lead_col(df)
    if lead is None:
        if "Bucket" not in df.columns:
            df["Bucket"] = "Unknown"
        return df
    # Compute via canonical bucket
    df["Bucket"] = df[lead].astype(str).apply(canonical_bucket)
    s = df[lead].astype(str).str.lower().fillna("")

    # Enforce GMC.com mapping
    mask_gmc = s.str.contains("gmc.com") | (s.str.contains("gmc") & (s.str.contains("offer raq") | s.str.contains("build your own") | s.str.contains("locate vehicle")))
    df.loc[mask_gmc, "Bucket"] = "GMC.com"

    # Dealer Website Leads additions
    mask_dwl = s.str.contains(r"amp") | s.str.contains("hand-raiser web") | s.str.contains("interactivetel") | s.str.contains("wallingford buick gmc - interactivetel")
    df.loc[mask_dwl, "Bucket"] = "Dealer Website Leads"

    # YouTube -> Social Media
    df.loc[s.str.contains("youtube"), "Bucket"] = "Social Media"

    # GM Lease / GM Loan-Payoff strict
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("loan") | s.str.contains("payoff") | s.str.contains("pay off")), "Bucket"] = "GM Loan/Payoff"

    # Credit Application consolidation
    df.loc[s.str.contains("credit") | s.str.contains("pre-qual") | s.str.contains("prequal") | s.str.contains("finance"), "Bucket"] = "Credit Application"

    # Carguru roll-up safety
    df.loc[s.str.contains("guru"), "Bucket"] = "Carguru"
    return df


    # Start with canonical mapping if available; otherwise pass-through
    try:
        df["Bucket"] = df[lead_col].astype(str).apply(canonical_bucket)
    except Exception:
        df["Bucket"] = df[lead_col].astype(str)

    # Enforce rollups that may not be covered by legacy buckets
    s = df[lead_col].astype(str).str.lower().fillna("")
    # GM Lease
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & s.str.contains("lease"), "Bucket"] = "GM Lease"
    # GM Loan/Payoff
    df.loc[(s.str.contains("gm") | s.str.contains("gm financial")) & (s.str.contains("payoff") | s.str.contains("pay off") | s.str.contains("loan")), "Bucket"] = "GM Loan/Payoff"
    # AMP -> Dealer Website Leads
    df.loc[s.str.contains(r"\bamp\b"), "Bucket"] = "Dealer Website Leads"
    # Credit Applications (finance terms)
    df.loc[s.str.contains("credit") | s.str.contains("pre-qual") | s.str.contains("prequal") | s.str.contains("finance"), "Bucket"] = "Credit Application"
    # Carguru roll-up
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


NON_INTERNET_SUBSTRINGS = [
    "walk-in","walk in","phone","service","service dept","body shop","parts",
    "bdc outbound","referral","repeat","repeat customer","fleet","event","employee",
    "unknown","record journal","playbook manifest","hill car","drive by","drive-by","drive by - location"
]
def looks_internet(bucket: str) -> bool:
    ss = (str(bucket) or "").lower()
    return not any(sub in ss for sub in NON_INTERNET_SUBSTRINGS)

