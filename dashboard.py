import streamlit as st
import pandas as pd
import sqlite3
import time
import io
from datetime import datetime

st.set_page_config(
    page_title="Content Moderation Monitor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #0d0f14; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem; max-width: 1500px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0a0c10 !important;
    border-right: 1px solid #1e2330;
}
[data-testid="stSidebar"] label { color: #94a3b8 !important; font-size: 0.75rem !important; }
[data-testid="stSidebar"] .stSelectbox > div > div { background: #111520; border-color: #1e2330; color: #e2e8f0; }
[data-testid="stSidebar"] .stSlider > div { color: #e2e8f0; }

/* Header */
.dash-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2330; }
.dash-title { font-size:1rem; font-weight:600; color:#e2e8f0; letter-spacing:0.08em; text-transform:uppercase; }
.dash-subtitle { font-size:0.65rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; margin-top:3px; }
.live-badge { display:inline-flex; align-items:center; gap:6px; background:#0f1a12; border:1px solid #1a3a1f; color:#4ade80; font-size:0.65rem; font-family:'IBM Plex Mono',monospace; font-weight:500; letter-spacing:0.1em; padding:4px 10px; border-radius:4px; }
.live-dot { width:6px; height:6px; background:#4ade80; border-radius:50%; animation:pulse 1.4s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Alert banner */
.alert-banner { display:flex; align-items:center; gap:10px; padding:0.75rem 1.1rem; border-radius:6px; margin-bottom:1.25rem; border:1px solid #4a1515; background:#1a0a0a; color:#f87171; font-size:0.8rem; font-family:'IBM Plex Mono',monospace; }
.alert-icon { font-size:1rem; }

/* Metric cards */
.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; margin-bottom:1.5rem; }
.metric-card { background:#111520; border:1px solid #1e2330; border-radius:8px; padding:1rem 1.1rem; }
.metric-label { font-size:0.62rem; font-weight:500; letter-spacing:0.12em; text-transform:uppercase; color:#4a5568; margin-bottom:0.4rem; }
.metric-value { font-size:1.6rem; font-weight:300; color:#e2e8f0; font-family:'IBM Plex Mono',monospace; line-height:1; }
.metric-value.danger{color:#f87171;} .metric-value.success{color:#4ade80;} .metric-value.warning{color:#fbbf24;} .metric-value.info{color:#60a5fa;}
.metric-sub { font-size:0.62rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; margin-top:5px; }

/* Section cards */
.section-card { background:#111520; border:1px solid #1e2330; border-radius:8px; padding:1.1rem 1.25rem; }
.section-title { font-size:0.65rem; font-weight:600; color:#94a3b8; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1rem; }

/* Alert rule cards */
.alert-rule { display:flex; align-items:center; justify-content:space-between; padding:0.65rem 0.9rem; background:#0d0f14; border:1px solid #1e2330; border-radius:6px; margin-bottom:6px; }
.alert-rule-name { font-size:0.75rem; color:#cbd5e1; font-weight:500; }
.alert-rule-desc { font-size:0.65rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; margin-top:2px; }
.alert-status-active { font-size:0.62rem; font-family:'IBM Plex Mono',monospace; color:#4ade80; background:#0a1f0f; border:1px solid #153522; padding:2px 8px; border-radius:3px; }
.alert-status-triggered { font-size:0.62rem; font-family:'IBM Plex Mono',monospace; color:#f87171; background:#2d0f0f; border:1px solid #4a1515; padding:2px 8px; border-radius:3px; }

/* Feed */
.feed-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem; }
.feed-title { font-size:0.65rem; font-weight:600; color:#94a3b8; letter-spacing:0.1em; text-transform:uppercase; }
.feed-ct { font-size:0.62rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; }
.feed-item { display:flex; align-items:center; gap:0.75rem; padding:0.7rem 0.9rem; border-radius:6px; margin-bottom:5px; border:1px solid #1e2330; border-left-width:3px; }
.feed-item.toxic { border-left-color:#ef4444; background:#130f0f; border-color:#2a1515; border-left-color:#ef4444; }
.feed-item.safe  { border-left-color:#22c55e; background:#0d1310; border-color:#152015; border-left-color:#22c55e; }
.feed-text { flex:1; font-size:0.75rem; color:#cbd5e1; line-height:1.4; }
.feed-meta { font-size:0.62rem; color:#4a5568; font-family:'IBM Plex Mono',monospace; white-space:nowrap; }
.feed-badge { font-size:0.58rem; font-family:'IBM Plex Mono',monospace; font-weight:500; letter-spacing:0.08em; padding:2px 7px; border-radius:3px; white-space:nowrap; }
.feed-badge.toxic { background:#2d0f0f; color:#f87171; border:1px solid #4a1515; }
.feed-badge.safe  { background:#0a1f0f; color:#4ade80; border:1px solid #153522; }
.feed-prob { font-size:0.62rem; font-family:'IBM Plex Mono',monospace; color:#4a5568; min-width:36px; text-align:right; }
.prob-bar-wrap { width:60px; height:3px; background:#1e2330; border-radius:2px; overflow:hidden; }
.prob-bar { height:100%; border-radius:2px; }
.prob-bar.toxic{background:#ef4444;} .prob-bar.safe{background:#22c55e;}

.empty-state { text-align:center; padding:3rem 2rem; color:#2d3748; font-size:0.8rem; font-family:'IBM Plex Mono',monospace; }

/* Sidebar section labels */
.sidebar-section { font-size:0.62rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:#4a5568; margin:1.25rem 0 0.5rem; padding-bottom:0.4rem; border-bottom:1px solid #1e2330; }
</style>
""", unsafe_allow_html=True)

# ── DB connection ─────────────────────────────────────────────────────────────
conn = sqlite3.connect("moderation.db", check_same_thread=False)

# ── Session state defaults ────────────────────────────────────────────────────
if "alert_log" not in st.session_state:
    st.session_state.alert_log = []
if "paused" not in st.session_state:
    st.session_state.paused = False

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ Controls")

    st.markdown('<div class="sidebar-section">Filters</div>', unsafe_allow_html=True)
    filter_prediction = st.selectbox("Show", ["All", "Toxic only", "Safe only"])
    search_query      = st.text_input("Search text", placeholder="keyword…")
    min_prob          = st.slider("Min toxicity probability", 0.0, 1.0, 0.0, 0.01)
    limit             = st.selectbox("Max rows", [20, 50, 100, 200], index=0)
    sort_by           = st.selectbox("Sort by", ["Newest first", "Oldest first", "Highest prob", "Lowest prob"])

    st.markdown('<div class="sidebar-section">Alert Rules</div>', unsafe_allow_html=True)
    alert_rate_thresh  = st.slider("Trigger if toxicity rate exceeds (%)", 0, 100, 30)
    alert_burst_thresh = st.slider("Trigger if toxic burst > N in last 20", 0, 20, 5)
    alert_prob_thresh  = st.slider("Trigger if avg prob exceeds", 0.0, 1.0, 0.7, 0.01)

    st.markdown('<div class="sidebar-section">Live Feed</div>', unsafe_allow_html=True)
    refresh_interval = st.selectbox("Refresh interval (s)", [1, 2, 5, 10], index=1)
    if st.button("⏸ Pause" if not st.session_state.paused else "▶ Resume"):
        st.session_state.paused = not st.session_state.paused

    st.markdown('<div class="sidebar-section">Export</div>', unsafe_allow_html=True)
    export_format = st.selectbox("Format", ["CSV", "JSON", "Excel"])

# ── Data fetch ────────────────────────────────────────────────────────────────
def fetch_data():
    try:
        base = "SELECT * FROM moderation_results"
        df = pd.read_sql_query(f"{base} ORDER BY id DESC LIMIT 500", conn)
    except Exception:
        cols = ["id", "text", "prediction", "toxic_probability"]
        df = pd.DataFrame(columns=cols)
    return df

def apply_filters(df):
    if filter_prediction == "Toxic only": df = df[df["prediction"] == "toxic"]
    elif filter_prediction == "Safe only": df = df[df["prediction"] == "safe"]
    if search_query:
        df = df[df["text"].str.contains(search_query, case=False, na=False)]
    df = df[df["toxic_probability"] >= min_prob]
    sort_map = {
        "Newest first":  ("id", False),
        "Oldest first":  ("id", True),
        "Highest prob":  ("toxic_probability", False),
        "Lowest prob":   ("toxic_probability", True),
    }
    col, asc = sort_map[sort_by]
    if col in df.columns:
        df = df.sort_values(col, ascending=asc)
    return df.head(limit)

def check_alerts(df_all):
    alerts = []
    total = len(df_all)
    if total == 0:
        return alerts
    toxic_count = len(df_all[df_all["prediction"] == "toxic"])
    rate = toxic_count / total * 100
    avg_prob = df_all["toxic_probability"].mean()
    burst = len(df_all.head(20)[df_all.head(20)["prediction"] == "toxic"])

    if rate > alert_rate_thresh:
        alerts.append(f"⚠ Toxicity rate {rate:.1f}% exceeds threshold ({alert_rate_thresh}%)")
    if burst > alert_burst_thresh:
        alerts.append(f"⚠ Burst: {burst} toxic in last 20 comments (threshold {alert_burst_thresh})")
    if avg_prob > alert_prob_thresh:
        alerts.append(f"⚠ Avg probability {avg_prob:.2f} exceeds threshold ({alert_prob_thresh})")
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
        return buf.getvalue(), "moderation_export.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# ── Main loop ─────────────────────────────────────────────────────────────────
placeholder = st.empty()

while True:
    if not st.session_state.paused:
        df_all      = fetch_data()
        df_filtered = apply_filters(df_all)
        active_alerts = check_alerts(df_all)

        # Accumulate alert log (max 50 entries)
        for a in active_alerts:
            entry = f"[{datetime.now().strftime('%H:%M:%S')}] {a}"
            if not st.session_state.alert_log or st.session_state.alert_log[0] != entry:
                st.session_state.alert_log.insert(0, entry)
        st.session_state.alert_log = st.session_state.alert_log[:50]

        total        = len(df_all)
        toxic_count  = len(df_all[df_all["prediction"] == "toxic"]) if total > 0 else 0
        safe_count   = len(df_all[df_all["prediction"] == "safe"])  if total > 0 else 0
        toxic_rate   = (toxic_count / total * 100) if total > 0 else 0
        avg_prob     = df_all["toxic_probability"].mean() if total > 0 else 0
        now          = datetime.now().strftime("%H:%M:%S")

        export_data, export_name, export_mime = build_export(df_filtered)

    with placeholder.container():

        # ── Header ───────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="dash-header">
          <div>
            <div class="dash-title">Content Moderation Monitor</div>
            <div class="dash-subtitle">Last updated · {now} · {"PAUSED" if st.session_state.paused else f"Refreshing every {refresh_interval}s"}</div>
          </div>
          <div class="live-badge">
            <div class="live-dot" style="{'animation:none;opacity:0.3' if st.session_state.paused else ''}"></div>
            {"PAUSED" if st.session_state.paused else "LIVE"}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Alert banners ─────────────────────────────────────────────────────
        for alert in active_alerts:
            st.markdown(f"""
            <div class="alert-banner">
              <span class="alert-icon">🔴</span>{alert}
            </div>
            """, unsafe_allow_html=True)

        # ── Metric cards ──────────────────────────────────────────────────────
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

        # ── Alert Rules (full width) ──────────────────────────────────────────
        st.markdown('<div class="section-card" style="margin-bottom:1rem">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Alert Rules</div>', unsafe_allow_html=True)

        rule_status = [
            ("Rate Threshold",  f"> {alert_rate_thresh}% toxicity rate",  toxic_rate > alert_rate_thresh),
            ("Burst Detector",  f"> {alert_burst_thresh} toxic in last 20", len(df_all.head(20)[df_all.head(20)["prediction"] == "toxic"]) > alert_burst_thresh if total > 0 else False),
            ("Avg Prob Alert",  f"avg prob > {alert_prob_thresh}",         avg_prob > alert_prob_thresh),
        ]
        rules_html = ""
        for name, desc, triggered in rule_status:
            status_html = '<span class="alert-status-triggered">TRIGGERED</span>' if triggered else '<span class="alert-status-active">ACTIVE</span>'
            rules_html += f"""
            <div class="alert-rule">
              <div>
                <div class="alert-rule-name">{name}</div>
                <div class="alert-rule-desc">{desc}</div>
              </div>
              {status_html}
            </div>"""
        st.markdown(rules_html, unsafe_allow_html=True)

        if st.session_state.alert_log:
            st.markdown('<div class="section-title" style="margin-top:1rem">Recent Alerts</div>', unsafe_allow_html=True)
            log_html = "".join(
                f'<div style="font-size:0.65rem;color:#f87171;font-family:IBM Plex Mono,monospace;padding:3px 0;border-bottom:1px solid #1e2330">{e}</div>'
                for e in st.session_state.alert_log[:6]
            )
            st.markdown(log_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Feed ──────────────────────────────────────────────────────────────
        n_filtered = len(df_filtered)
        st.markdown(f"""
        <div class="feed-header" style="margin-top:1rem">
          <div class="feed-title">Live Moderation Feed
            {"· <span style='color:#fbbf24'>filtered</span>" if filter_prediction != 'All' or search_query or min_prob > 0 else ""}
          </div>
          <div class="feed-ct">Showing {n_filtered} of {total} · {sort_by.lower()}</div>
        </div>
        """, unsafe_allow_html=True)

        if n_filtered == 0:
            st.markdown('<div class="empty-state">no results match current filters</div>', unsafe_allow_html=True)
        else:
            feed_html = ""
            for _, row in df_filtered.iterrows():
                text       = str(row["text"])
                prediction = str(row["prediction"])
                prob       = float(row["toxic_probability"])
                bar_w      = int(prob * 100)
                item_cls   = "toxic" if prediction == "toxic" else "safe"
                badge      = "TOXIC" if prediction == "toxic" else "SAFE"
                display_t  = text[:110] + "…" if len(text) > 110 else text
                feed_html += f"""
                <div class="feed-item {item_cls}">
                  <div class="feed-text">{display_t}</div>
                  <div class="prob-bar-wrap"><div class="prob-bar {item_cls}" style="width:{bar_w}%"></div></div>
                  <div class="feed-prob">{prob:.2f}</div>
                  <div class="feed-badge {item_cls}">{badge}</div>
                </div>"""
            st.markdown(feed_html, unsafe_allow_html=True)

        # ── Export button ─────────────────────────────────────────────────────
        st.markdown("<div style='margin-top:1.25rem'>", unsafe_allow_html=True)
        st.download_button(
            label=f"⬇ Export {n_filtered} rows as {export_format}",
            data=export_data,
            file_name=export_name,
            mime=export_mime,
            use_container_width=False,
            key=f"export_{export_format}_{n_filtered}_{now}",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    time.sleep(refresh_interval)