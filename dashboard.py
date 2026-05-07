import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Content Moderation Monitor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #0d0f14; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem; max-width: 1500px; }

[data-testid="stSidebar"] { background: #0a0c10 !important; border-right: 1px solid #1e2330; }
[data-testid="stSidebar"] label { color: #94a3b8 !important; font-size: 0.75rem !important; }
[data-testid="stSidebar"] .stSelectbox > div > div { background: #111520; border-color: #1e2330; color: #e2e8f0; }
[data-testid="stSidebar"] .stSlider > div { color: #e2e8f0; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #94a3b8 !important; font-size: 0.7rem !important; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; }

/* Header */
.dash-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2330; }
.dash-title { font-size:1rem; font-weight:600; color:#e2e8f0; letter-spacing:0.08em; text-transform:uppercase; }
.dash-subtitle { font-size:0.65rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; margin-top:3px; }
.live-badge { display:inline-flex; align-items:center; gap:6px; background:#0f1a12; border:1px solid #1a3a1f; color:#4ade80; font-size:0.65rem; font-family:'IBM Plex Mono',monospace; font-weight:500; letter-spacing:0.1em; padding:4px 10px; border-radius:4px; }
.live-dot { width:6px; height:6px; background:#4ade80; border-radius:50%; animation:pulse 1.4s infinite; }
.paused-badge { display:inline-flex; align-items:center; gap:6px; background:#1a1400; border:1px solid #3d2a00; color:#fbbf24; font-size:0.65rem; font-family:'IBM Plex Mono',monospace; font-weight:500; letter-spacing:0.1em; padding:4px 10px; border-radius:4px; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Alert banner */
.alert-banner { display:flex; align-items:center; gap:10px; padding:0.7rem 1rem; border-radius:6px; margin-bottom:0.6rem; border:1px solid #4a1515; background:#1a0a0a; color:#f87171; font-size:0.75rem; font-family:'IBM Plex Mono',monospace; }

/* Metric cards */
.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; margin-bottom:1.5rem; }
.metric-card { background:#111520; border:1px solid #1e2330; border-radius:8px; padding:1rem 1.1rem; }
.metric-label { font-size:0.62rem; font-weight:500; letter-spacing:0.12em; text-transform:uppercase; color:#4a5568; margin-bottom:0.4rem; }
.metric-value { font-size:1.7rem; font-weight:300; color:#e2e8f0; font-family:'IBM Plex Mono',monospace; line-height:1; }
.metric-value.danger { color:#f87171; }
.metric-value.success { color:#4ade80; }
.metric-value.warning { color:#fbbf24; }
.metric-sub { font-size:0.6rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; margin-top:5px; }

/* Section card */
.section-card { background:#111520; border:1px solid #1e2330; border-radius:8px; padding:1.1rem 1.25rem; margin-bottom:1rem; }
.section-title { font-size:0.65rem; font-weight:600; color:#94a3b8; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.85rem; }

/* Alert rules */
.alert-rule { display:flex; align-items:center; justify-content:space-between; padding:0.6rem 0.85rem; background:#0d0f14; border:1px solid #1e2330; border-radius:6px; margin-bottom:5px; }
.alert-rule-name { font-size:0.75rem; color:#cbd5e1; font-weight:500; }
.alert-rule-desc { font-size:0.62rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; margin-top:2px; }
.alert-status-active { font-size:0.6rem; font-family:'IBM Plex Mono',monospace; color:#4ade80; background:#0a1f0f; border:1px solid #153522; padding:2px 8px; border-radius:3px; }
.alert-status-triggered { font-size:0.6rem; font-family:'IBM Plex Mono',monospace; color:#f87171; background:#2d0f0f; border:1px solid #4a1515; padding:2px 8px; border-radius:3px; }
.alert-log-row { font-size:0.63rem; color:#f87171; font-family:'IBM Plex Mono',monospace; padding:4px 0; border-bottom:1px solid #1a1e2a; }

/* Feed */
.feed-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.65rem; }
.feed-title { font-size:0.65rem; font-weight:600; color:#94a3b8; letter-spacing:0.1em; text-transform:uppercase; }
.feed-ct { font-size:0.62rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; }
.feed-item { display:flex; align-items:center; gap:0.75rem; padding:0.7rem 0.9rem; border-radius:6px; margin-bottom:5px; border:1px solid; border-left-width:3px; }
.feed-item.toxic { border-color:#2a1515; border-left-color:#ef4444; background:#130f0f; }
.feed-item.safe  { border-color:#152015; border-left-color:#22c55e; background:#0d1310; }
.feed-text { flex:1; font-size:0.78rem; color:#cbd5e1; line-height:1.45; }
.feed-badge { font-size:0.58rem; font-family:'IBM Plex Mono',monospace; font-weight:500; letter-spacing:0.08em; padding:2px 8px; border-radius:3px; white-space:nowrap; }
.feed-badge.toxic { background:#2d0f0f; color:#f87171; border:1px solid #4a1515; }
.feed-badge.safe  { background:#0a1f0f; color:#4ade80; border:1px solid #153522; }
.feed-prob { font-size:0.62rem; font-family:'IBM Plex Mono',monospace; color:#4a5568; min-width:36px; text-align:right; }
.prob-bar-wrap { width:64px; height:3px; background:#1e2330; border-radius:2px; overflow:hidden; }
.prob-bar { height:100%; border-radius:2px; }
.prob-bar.toxic { background:#ef4444; }
.prob-bar.safe  { background:#22c55e; }

.empty-state { text-align:center; padding:3rem 2rem; color:#2d3748; font-size:0.8rem; font-family:'IBM Plex Mono',monospace; }

/* Download button */
.stDownloadButton > button {
    background: #0a1f0f !important;
    border: 1px solid #153522 !important;
    color: #4ade80 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em;
    border-radius: 5px !important;
    padding: 0.45rem 1.1rem !important;
}
.stDownloadButton > button:hover {
    background: #0f2a18 !important;
    border-color: #22c55e !important;
}
</style>
""", unsafe_allow_html=True)

# ── DB ────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return sqlite3.connect("moderation.db", check_same_thread=False)

conn = get_connection()

# ── Session state ─────────────────────────────────────────────────────────────
if "alert_log" not in st.session_state:
    st.session_state.alert_log = []
if "paused" not in st.session_state:
    st.session_state.paused = False

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ Controls")

    st.markdown("### Filters")
    filter_prediction = st.selectbox("Show", ["All", "Toxic only", "Safe only"])
    search_query      = st.text_input("Search text", placeholder="keyword…")
    min_prob          = st.slider("Min toxicity probability", 0.0, 1.0, 0.0, 0.01)
    limit             = st.selectbox("Max rows", [20, 50, 100, 200], index=0)
    sort_by           = st.selectbox("Sort by", ["Newest first", "Oldest first", "Highest prob", "Lowest prob"])

    st.markdown("### Alert Thresholds")
    alert_rate_thresh  = st.slider("Toxicity rate % trigger", 0, 100, 30)
    alert_burst_thresh = st.slider("Burst count trigger (last 20)", 0, 20, 5)
    alert_prob_thresh  = st.slider("Avg probability trigger", 0.0, 1.0, 0.70, 0.01)

    st.markdown("### Live Feed")
    refresh_interval = st.selectbox("Refresh interval (s)", [1, 2, 5, 10], index=1)
    if st.button("⏸ Pause" if not st.session_state.paused else "▶ Resume", use_container_width=True):
        st.session_state.paused = not st.session_state.paused

    st.markdown("### Export")
    export_format = st.selectbox("Format", ["CSV", "JSON", "Excel"])

# ── Auto-refresh (only when not paused) ──────────────────────────────────────
if not st.session_state.paused:
    st_autorefresh(interval=refresh_interval * 1000, key="autorefresh")

# ── Data helpers ──────────────────────────────────────────────────────────────
def fetch_data():
    try:
        return pd.read_sql_query(
            "SELECT * FROM moderation_results ORDER BY id DESC LIMIT 500", conn
        )
    except Exception:
        return pd.DataFrame(columns=["id", "text", "prediction", "toxic_probability"])

def apply_filters(df):
    if filter_prediction == "Toxic only":
        df = df[df["prediction"] == "toxic"]
    elif filter_prediction == "Safe only":
        df = df[df["prediction"] == "safe"]
    if search_query:
        df = df[df["text"].str.contains(search_query, case=False, na=False)]
    df = df[df["toxic_probability"] >= min_prob]
    sort_map = {
        "Newest first": ("id", False),
        "Oldest first": ("id", True),
        "Highest prob": ("toxic_probability", False),
        "Lowest prob":  ("toxic_probability", True),
    }
    col, asc = sort_map[sort_by]
    if col in df.columns:
        df = df.sort_values(col, ascending=asc)
    return df.head(limit)

def check_alerts(df_all):
    alerts = []
    if len(df_all) == 0:
        return alerts
    total     = len(df_all)
    toxic_ct  = len(df_all[df_all["prediction"] == "toxic"])
    rate      = toxic_ct / total * 100
    avg_p     = df_all["toxic_probability"].mean()
    burst     = len(df_all.head(20)[df_all.head(20)["prediction"] == "toxic"])
    if rate  > alert_rate_thresh:  alerts.append(f"⚠  Toxicity rate {rate:.1f}% exceeds threshold ({alert_rate_thresh}%)")
    if burst > alert_burst_thresh: alerts.append(f"⚠  Burst: {burst} toxic in last 20 comments (threshold {alert_burst_thresh})")
    if avg_p > alert_prob_thresh:  alerts.append(f"⚠  Avg probability {avg_p:.2f} exceeds threshold ({alert_prob_thresh})")
    return alerts

def build_export(df):
    if export_format == "CSV":
        return df.to_csv(index=False).encode(), "moderation_export.csv", "text/csv"
    elif export_format == "JSON":
        return df.to_json(orient="records", indent=2).encode(), "moderation_export.json", "application/json"
    else:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Moderation")
        return buf.getvalue(), "moderation_export.xlsx", \
               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# ── Fetch & compute ───────────────────────────────────────────────────────────
df_all      = fetch_data()
df_filtered = apply_filters(df_all)
active_alerts = check_alerts(df_all)

total       = len(df_all)
toxic_count = len(df_all[df_all["prediction"] == "toxic"]) if total else 0
safe_count  = len(df_all[df_all["prediction"] == "safe"])  if total else 0
toxic_rate  = (toxic_count / total * 100) if total else 0
avg_prob    = df_all["toxic_probability"].mean() if total else 0
n_filtered  = len(df_filtered)
now         = datetime.now().strftime("%H:%M:%S")

# Accumulate alert log
for a in active_alerts:
    entry = f"[{now}] {a}"
    if not st.session_state.alert_log or st.session_state.alert_log[0] != entry:
        st.session_state.alert_log.insert(0, entry)
st.session_state.alert_log = st.session_state.alert_log[:50]

export_data, export_name, export_mime = build_export(df_filtered)

# ── HEADER ────────────────────────────────────────────────────────────────────
badge = '<div class="paused-badge">⏸ PAUSED</div>' if st.session_state.paused else \
        '<div class="live-badge"><div class="live-dot"></div>LIVE</div>'

st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Content Moderation Monitor</div>
    <div class="dash-subtitle">Last updated · {now} · {"paused" if st.session_state.paused else f"refreshing every {refresh_interval}s"}</div>
  </div>
  {badge}
</div>
""", unsafe_allow_html=True)

# ── ALERT BANNERS ─────────────────────────────────────────────────────────────
for alert in active_alerts:
    st.markdown(f'<div class="alert-banner">🔴 &nbsp;{alert}</div>', unsafe_allow_html=True)

# ── METRICS ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">Total Analyzed</div>
    <div class="metric-value">{total:,}</div>
    <div class="metric-sub">all time</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Toxic</div>
    <div class="metric-value danger">{toxic_count:,}</div>
    <div class="metric-sub">flagged</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Safe</div>
    <div class="metric-value success">{safe_count:,}</div>
    <div class="metric-sub">approved</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Toxicity Rate</div>
    <div class="metric-value warning">{toxic_rate:.1f}<span style="font-size:1rem;color:#4a5568">%</span></div>
    <div class="metric-sub">avg prob · {avg_prob:.2f}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── ALERT RULES + LOG ─────────────────────────────────────────────────────────
burst_now = len(df_all.head(20)[df_all.head(20)["prediction"] == "toxic"]) if total else 0
rule_status = [
    ("Rate Threshold", f"> {alert_rate_thresh}% toxicity rate",       toxic_rate  > alert_rate_thresh),
    ("Burst Detector", f"> {alert_burst_thresh} toxic in last 20",     burst_now   > alert_burst_thresh),
    ("Avg Prob Alert", f"avg prob > {alert_prob_thresh}",              avg_prob    > alert_prob_thresh),
]

rules_html = ""
for name, desc, triggered in rule_status:
    status = '<span class="alert-status-triggered">TRIGGERED</span>' if triggered \
             else '<span class="alert-status-active">ACTIVE</span>'
    rules_html += f"""
    <div class="alert-rule">
      <div>
        <div class="alert-rule-name">{name}</div>
        <div class="alert-rule-desc">{desc}</div>
      </div>
      {status}
    </div>"""

log_html = ""
if st.session_state.alert_log:
    log_rows = "".join(
        f'<div class="alert-log-row">{e}</div>'
        for e in st.session_state.alert_log[:6]
    )
    log_html = f'<div class="section-title" style="margin-top:1rem">Recent Alert Log</div>{log_rows}'

import textwrap

rules_html = textwrap.dedent(rules_html)

st.markdown(f"""
<div class="section-card">
  <div class="section-title">Alert Rules</div>
  {rules_html}
  {log_html}
</div>
""", unsafe_allow_html=True)
# ── FEED ──────────────────────────────────────────────────────────────────────
filtered_label = "· <span style='color:#fbbf24'>filtered</span>" \
    if (filter_prediction != "All" or search_query or min_prob > 0) else ""

st.markdown(f"""
<div class="feed-header">
  <div class="feed-title">Live Moderation Feed {filtered_label}</div>
  <div class="feed-ct">Showing {n_filtered} of {total:,} · {sort_by.lower()}</div>
</div>
""", unsafe_allow_html=True)

if n_filtered == 0:
    st.markdown('<div class="empty-state">no results match current filters</div>', unsafe_allow_html=True)
else:
    feed_html = ""
    for _, row in df_filtered.iterrows():
        text      = str(row["text"])
        pred      = str(row["prediction"])
        prob      = float(row["toxic_probability"])
        cls       = "toxic" if pred == "toxic" else "safe"
        badge_lbl = "TOXIC" if pred == "toxic" else "SAFE"
        display   = text[:115] + "…" if len(text) > 115 else text
        bar_w     = int(prob * 100)
        feed_html += f"""
        <div class="feed-item {cls}">
          <div class="feed-text">{display}</div>
          <div class="prob-bar-wrap"><div class="prob-bar {cls}" style="width:{bar_w}%"></div></div>
          <div class="feed-prob">{prob:.2f}</div>
          <div class="feed-badge {cls}">{badge_lbl}</div>
        </div>"""
    st.markdown(feed_html, unsafe_allow_html=True)

# ── EXPORT ────────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:1.25rem'></div>", unsafe_allow_html=True)
st.download_button(
    label=f"⬇  Export {n_filtered} rows as {export_format}",
    data=export_data,
    file_name=export_name,
    mime=export_mime,
    key=f"dl_{export_format}_{n_filtered}_{now}",
)