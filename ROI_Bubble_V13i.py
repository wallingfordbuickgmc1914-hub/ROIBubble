
import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px

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
  max-height: 540px;
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
    n = _normalize_spaces(nraw)
    if n == "total":
        return "TOTAL"
    if n.startswith("carbravo drp"):
        return "CarBravo DRP"
    if n.startswith("scd") or "shop click drive" in n:
        return "Shop Click Drive"
    if ("wallingfordgmc.com" in n) or ("wallingfordbuickgmc.com" in n) or ("ansira" in n) or n.startswith("do -") or ("gm dealer website" in n):
        return "Dealer Website Leads"
    if "autoweb" in n: return "Autoweb"
    if "carfax" in n: return "CarFax"
    if "cargurus" in n or "car gurus" in n: return "Cargurus"
    if "cars.com" in n or "carscom" in n: return "Cars.com"
    if "autotrader" in n or "auto trader" in n: return "AutoTrader"
    if "gm 3rd party" in n or "gm third party" in n or "gm 3rd" in n: return "GM Third Party"
    if "trade pending" in n or "tradepending" in n: return "Trade Pending"
    if "truecar" in n or "true car" in n: return "TrueCar"
    if "podium" in n: return "Podium"
    return nraw or "Unknown"

# Non-internet markers
NON_INTERNET_SUBSTRINGS = [
    "walk-in", "walk in", "showroom", "service", "gm service", "service dept",
    "repeat", "referral", "phone up", "phone-up", "equity", "event", "parts",
    "hill car", "used car event", "drive by", "driveby"
]

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
    if f_new: 
        df_n=read_report(f_new); df_n["__dataset__"]="New/Combined"; data_frames.append(df_n)
    if f_used:
        df_u=read_report(f_used); df_u["__dataset__"]="Used"; data_frames.append(df_u)
elif mode=="Monthly files":
    sel=st.sidebar.multiselect("Months to include", months_all, default=["Jan","Feb","Mar"])
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
    if isinstance(v, tuple) and v[0]=="per_sale":
        st.session_state.cost_inputs[k]=("per_sale", st.sidebar.number_input(f"{k} — per sale", min_value=0, value=int(v[1]), step=10, key=f"c_{k}"))
    else:
        st.session_state.cost_inputs[k]=st.sidebar.number_input(f"{k} — monthly", min_value=0, value=int(v), step=50, key=f"c_{k}")

# ---------- Assemble ----------
if len(data_frames)==0:
    st.info("Upload at least one file to begin."); st.stop()

df_all=pd.concat(data_frames, ignore_index=True)

# Filter out any "Credit" sources entirely
df_all = df_all[~df_all["Lead Source"].fillna("").str.contains("credit", case=False, regex=False)]

if exclude_weak:
    df_all=df_all[~df_all["Lead Source"].fillna("").str.contains("Weak To Ask", case=False, regex=False)]

def months_between(s, e):
    if s not in months_all or e not in months_all: return 1
    return (months_all.index(e)-months_all.index(s))+1
window_months = months_between(start_m, end_m)

def compute_cost(bucket, sold):
    ci=st.session_state.cost_inputs
    if bucket not in ci:
        if "podium" in (bucket or "").lower():
            v = 1500
        else:
            return 0.0
    else:
        v = ci[bucket]
    if isinstance(v, tuple) and v[0]=="per_sale":
        return float(v[1])*(sold or 0)
    months_factor = window_months
    return float(v)*months_factor

def compute_agg(df):
    agg=df.groupby(["Bucket"], dropna=False).agg(
        Leads=("Total Leads","sum"),
        Sold=("Sold in Timeframe","sum"),
        ApptsSet=("Appts Set","sum"),
        ApptsShown=("Appts Shown","sum"),
    ).reset_index()
    agg["__internet__"]=agg["Bucket"].astype(str).apply(looks_internet)
    agg=agg[agg["Bucket"].str.upper()!="TOTAL"]
    has_used = "__dataset__" in df.columns and (df["__dataset__"]=="Used").any()
    use_pru = (pru_used if has_used and pru_used>0 else pru_combined)
    agg["PRU"]=use_pru
    agg["Profit"]=agg["Sold"]*agg["PRU"]
    agg["Cost"]=agg.apply(lambda r: compute_cost(r["Bucket"], r["Sold"]), axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        roix=np.where(agg["Cost"]>0, agg["Profit"]/agg["Cost"], agg["Sold"]*1.0)
    agg["ROIx"]=roix
    agg["LeadToSale%"]=np.where(agg["Leads"]>0, agg["Sold"]/agg["Leads"]*100.0, 0.0)
    agg["ApptSet%"]=np.where(agg["Leads"]>0, agg["ApptsSet"]/agg["Leads"]*100.0, 0.0)
    agg["Contacts"]=agg["ApptsSet"]
    agg=agg[agg["Sold"]>0].copy()
    agg["__is_paid__"]=agg["Cost"]>0
    agg["NetProfit"]=agg["Profit"]-agg["Cost"]
    return agg

agg=compute_agg(df_all)


# ---------- Title & Inline Info ----------
title_col, info_col = st.columns([0.92, 0.08])
with title_col:
    st.markdown("# Lead ROI Bubble Map")
with info_col:
    with st.expander("ℹ️ Filters & Grouping (click)"):
        st.markdown("""
**This dashboard applies the following rules:**

**Filtered out entirely**
- Any source containing **"Credit"**
- \*Optionally\*: `* I Was Too Weak To Ask` (when the sidebar box is checked)

**"Only Internet" toggle excludes these non‑internet buckets**
- **Service / Service Dept / GM Service**
- **Hill Car** (and related: Hill RBC / Hill SVC / Hill MCY)
- **Repeat Customer** / **Referral**
- **Drive By / Drive  By / DriveBy** (any spacing)
- Other walk‑in style terms: *Walk‑In/Showroom/Phone Up/Equity/Event/Parts/Used Car Event*

**Source grouping (buckets)**
- **TrueCar** → All TrueCar variants grouped; default cost: **$349 per sale**
- **Trade Pending** → Any source containing "TradePending" or "Trade Pending"
- **Dealer Website Leads** → wallingfordgmc.com / wallingfordbuickgmc.com / Ansira / DO – " " / GM Dealer Website
- **Podium** → Any source containing "Podium" (default monthly cost: **$1,500**)
- **CarBravo DRP** → Sources starting with "CarBravo DRP"
- **Shop Click Drive** → Sources starting with "SCD" or containing "Shop Click Drive"

**Paid sources**
- A bucket is **Paid** only when its **computed Cost > 0** for the current view (window‑scaled monthly cost or per‑sale cost × Sold).
""")

# ---------- Title Hotlist ----------
internet_base = agg[agg["__internet__"]].copy()
bucket_count = internet_base.shape[0]
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
    only_internet = st.toggle("Only Internet (vs All source types)", value=True)
    paid_only = st.toggle("Paid sources only", value=False)
    base = agg[agg["__internet__"]] if only_internet else agg.copy()
    view = base if not paid_only else base[base["__is_paid__"]].copy()

    st.markdown("## Effectiveness Bubble Map")

    def roix_norm_static(x):
        if not np.isfinite(x): x=10.0
        x = max(0.0, min(float(x), 10.0))
        if x<=1.0: return 0.25*(x/1.0)
        return 0.25 + 0.75*((x-1.0)/9.0)

    plot=view.copy()
    plot["color_norm"]=plot["ROIx"].apply(roix_norm_static)
    plot["size_val"]=plot["ROIx"].apply(lambda v: 1.3*max(0.5, min(v, 10.0)))
    plot["Sold%"]=np.where(plot["Leads"]>0, plot["Sold"]/plot["Leads"]*100.0, 0.0)
    plot["hover"]= (
        "<b>"+plot["Bucket"].astype(str)+"</b><br>"
        "ROI: "+plot["ROIx"].map(roix_label)+"<br>"
        "Profit: "+plot["Profit"].map(money0)+"<br>"
        "Cost: "+plot["Cost"].map(money0)+"<br>"
        "Sold %: "+plot["Sold%"].map(lambda x: pct2(x, cap_100=True))+"<br>"
        "Leads: "+plot["Leads"].map(num0)+"<br>"
        "Contacts: "+plot["Contacts"].map(num0)+" (Appts Set)"
    )
    plot["label"]=plot["ROIx"].apply(roix_label)

    colorscale=[(0.00,"#c0392b"), (0.10,"#e67e22"), (0.24,"#f1c40f"), (0.25,"#8fd694"), (0.60,"#2e7d32"), (1.00,"#1b5e20")]
    fixed_ticks=[0,0.5,1,2,4,6,8,10]
    tickvals=[roix_norm_static(t) for t in fixed_ticks]
    ticktext=[("10x+" if t==10 else ("{:.2f}x".format(t) if t<1 else "{}x".format(int(t)))) for t in fixed_ticks]

    fig=px.scatter(
        plot, x="LeadToSale%", y="Contacts", size="size_val", color="color_norm",
        text="label", custom_data=["hover","Bucket"],
        labels={"LeadToSale%":"Lead → Sale %", "Contacts":"Internet Contacts (Appts Set)"},
        color_continuous_scale=colorscale, range_color=(0.0,1.0)
    )
    fig.update_traces(marker=dict(opacity=0.92, line=dict(width=1, color="rgba(0,0,0,0.35)")),
                      textposition="top center",
                      hovertemplate="%{customdata[0]}<extra></extra>")
    fig.update_layout(hoverlabel=dict(bgcolor="rgba(22,22,22,0.95)", font_size=13),
                      height=760,
                      coloraxis_colorbar=dict(title="ROI (x)", tickvals=tickvals, ticktext=ticktext))
    st.plotly_chart(fig, use_container_width=True)

    # Totals
    st.markdown("#### Totals for this view")
    leads= view["Leads"].sum(); sold=view["Sold"].sum()
    profit=view["Profit"].sum(); cost=view["Cost"].sum()
    roix_total=(profit/cost) if cost>0 else float(sold) if sold>0 else 0.0
    soldpct=(sold/leads*100.0) if leads>0 else 0.0
    a,b,c,d,e,f=st.columns(6)
    a.metric("Leads", num0(leads))
    b.metric("Sold (units)", num0(sold))
    c.metric("Sold %", pct2(soldpct, cap_100=True))
    d.metric("Profit", money0(profit))
    e.metric("Cost", money0(cost))
    f.metric("ROI", roix_label(roix_total))

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
        st.markdown('<div id="top10-scroll">', unsafe_allow_html=True)
        for _,r in top.iterrows():
            is_unpaid = (r['Cost']<=0)
            gray = "opacity:.55;filter:grayscale(50%);" if is_unpaid else ""
            badge = '<span class="badge">No cost</span>' if is_unpaid else ""
            st.markdown(f"""
<div class="card" style="{gray}">
  <div style="font-weight:800;margin-bottom:4px">{r['Bucket']}{badge}</div>
  <div>ROI: <b>{roix_label(r['ROIx'])}</b></div>
  <div>Profit: {money0(r['Profit'])} - Cost: {money0(r['Cost'])}</div>
  <div>Sold: {num0(r['Sold'])} - Leads: {num0(r['Leads'])}</div>
  <div>Lead→Sale: {pct2((r['Sold']/r['Leads']*100.0) if r['Leads']>0 else 0, cap_100=True)} - Contacts: {num0(r['ApptsSet'])}</div>
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Note: grayed cards are unpaid (Cost = $0).")
    else:
        st.info("No sources to display.")

# ---------- Details ----------
st.markdown("---")
st.markdown("## Details")
bucket_opts = agg[agg["__internet__"]]["Bucket"].tolist()
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
