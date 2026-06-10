"""
pages/6_📱_Session_Analysis.py — Session Analytics
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all
from shared_styles import inject_shared_styles, inject_sidebar_brand

st.set_page_config(page_title="BOC · Session Analysis", page_icon="📱", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#FFFFFF;color:#1E293B;}
.page-title{font-size:2rem;font-weight:800;color:#1E293B;margin-bottom:0.2rem;}
.page-sub{color:#64748B;font-size:0.95rem;margin-bottom:1.5rem;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F172A,#1E293B) !important;
  border-right:1px solid #334155;}
.sess-kpi{background:#FFFFFF;
  border:1px solid #E2E8F0;border-radius:16px;padding:1.2rem 1rem;
  text-align:center;position:relative;overflow:hidden;
  box-shadow:0 1px 3px rgba(0,0,0,0.06);}
.sess-kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,#CBD5E1,#94A3B8);}
.sess-kpi-val{font-size:1.8rem;font-weight:900;color:#1E293B;}
.sess-kpi-lbl{font-size:0.7rem;text-transform:uppercase;letter-spacing:1.2px;color:#94A3B8;margin-top:2px;}
.sess-kpi-desc{font-size:0.7rem;color:#64748B;margin-top:4px;line-height:1.3;}
.section-desc{background:linear-gradient(135deg,rgba(124,58,237,0.04),rgba(34,211,238,0.04));
  border-left:3px solid #7C3AED;padding:0.8rem 1.2rem;border-radius:0 8px 8px 0;
  margin-bottom:1rem;font-size:0.88rem;color:#475569;line-height:1.6;}
</style>
""", unsafe_allow_html=True)

inject_shared_styles()
inject_sidebar_brand()

dfs = load_all()
session = dfs.get("session", pd.DataFrame())
user = dfs.get("user", pd.DataFrame())

st.markdown('<div class="page-title">📱 Session Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Login patterns, device analytics, and user engagement insights from session data</div>', unsafe_allow_html=True)

if session.empty:
    st.warning("No session data found.")
    st.stop()

# ── Data Prep ─────────────────────────────────────────────────────────────────
sess_all = session.copy()
sess_all["createdAt"] = pd.to_datetime(sess_all["createdAt"], errors="coerce")
sess_all = sess_all.dropna(subset=["createdAt"])
sess_all["date"] = sess_all["createdAt"].dt.date

min_date = sess_all["date"].min()
max_date = sess_all["date"].max()

def parse_device(ua):
    if not isinstance(ua, str):
        return "Unknown"
    ua_lower = ua.lower()
    if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower or "ipad" in ua_lower:
        return "Mobile"
    return "Desktop"

def parse_os(ua):
    if not isinstance(ua, str):
        return "Other"
    if "Android" in ua:
        return "Android"
    elif "Windows" in ua:
        return "Windows"
    elif "iPhone" in ua or "iPad" in ua:
        return "iOS"
    elif "Macintosh" in ua or "macOS" in ua:
        return "macOS"
    elif "Linux" in ua:
        return "Linux"
    return "Other"

def parse_browser(ua):
    if not isinstance(ua, str):
        return "Other"
    if "Edg/" in ua:
        return "Edge"
    elif "OPR/" in ua or "Opera" in ua:
        return "Opera"
    elif "SamsungBrowser" in ua:
        return "Samsung"
    elif "Firefox/" in ua:
        return "Firefox"
    elif "Chrome/" in ua:
        return "Chrome"
    elif "Safari/" in ua:
        return "Safari"
    return "Other"

sess_all["device"] = sess_all["userAgent"].apply(parse_device)
sess_all["os"] = sess_all["userAgent"].apply(parse_os)
sess_all["browser"] = sess_all["userAgent"].apply(parse_browser)
sess_all["hour"] = sess_all["createdAt"].dt.hour
sess_all["day_of_week"] = sess_all["createdAt"].dt.day_name()

total_sessions = len(sess_all)
unique_users = sess_all["userId"].nunique()
mobile_pct = (sess_all["device"] == "Mobile").sum() / total_sessions * 100 if total_sessions > 0 else 0

# ── Section 1: Login Activity Trends ─────────────────────────────────────────
st.markdown("### 📈 Login Activity Trends")
st.markdown("""<div class="section-desc">
<strong>Daily login volume</strong> reveals platform engagement patterns over time. Sudden spikes may indicate
marketing campaigns, app releases, or viral events. Use the <strong>date range filter</strong> below to zoom
into a specific period. The <strong>hourly distribution</strong> shows which hours see the most logins for a
selected date — useful for scheduling maintenance windows and push notifications.
</div>""", unsafe_allow_html=True)

# ── Inline Date Range Filter (From / To) ─────────────────────────────────────
fc1, fc2, _sp = st.columns([2, 2, 6])
with fc1:
    date_start = st.date_input("📅 From", value=min_date, min_value=min_date, max_value=max_date, key="sess_from")
with fc2:
    date_end = st.date_input("📅 To", value=max_date, min_value=min_date, max_value=max_date, key="sess_to")

if date_start > date_end:
    st.error("Start date must be before end date.")
    st.stop()

st.caption(f"ℹ️ Data available: {min_date.strftime('%b %d, %Y')} — {max_date.strftime('%b %d, %Y')}")

# Filter for daily volume
sess_range = sess_all[(sess_all["date"] >= date_start) & (sess_all["date"] <= date_end)].copy()

if sess_range.empty:
    st.warning("No sessions found for the selected date range.")
    st.stop()

# ── Row 1: Daily Login Volume + Hourly Distribution ──────────────────────────
r1c1, r1c2 = st.columns(2)

with r1c1:
    daily = sess_range.groupby("date").size().reset_index(name="sessions")
    daily["date"] = pd.to_datetime(daily["date"])
    peak_date = daily.loc[daily["sessions"].idxmax()]

    fig_daily = go.Figure()
    fig_daily.add_trace(go.Bar(
        x=daily["date"], y=daily["sessions"],
        marker=dict(color="#7C3AED", opacity=0.85),
        name="Sessions",
    ))
    fig_daily.add_annotation(
        x=peak_date["date"], y=peak_date["sessions"],
        text=f"Peak: {int(peak_date['sessions'])}",
        showarrow=True, arrowhead=2, arrowcolor="#F97316",
        font=dict(color="#F97316", size=11, family="Inter"),
        ax=0, ay=-30,
    )
    range_total = len(sess_range)
    range_users = sess_range["userId"].nunique()
    fig_daily.update_layout(
        title=f"📅 Daily Login Volume  ({range_total:,} sessions, {range_users:,} users)",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"), title_font=dict(color="#1E293B", size=14),
        height=420, margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(title="Date", gridcolor="rgba(0,0,0,0.06)"),
        yaxis=dict(title="Sessions", gridcolor="rgba(0,0,0,0.06)"),
    )
    st.plotly_chart(fig_daily, width='stretch')

with r1c2:
    # Single date picker for hourly distribution
    available_dates = sorted(sess_range["date"].unique())
    sel_date = st.date_input("📅 Select date for hourly breakdown", value=available_dates[-1],
                             min_value=date_start, max_value=date_end, key="sess_hour_date")

    sess_day = sess_range[sess_range["date"] == sel_date]

    if len(sess_day) > 0:
        hourly = sess_day.groupby("hour").size().reindex(range(24), fill_value=0).reset_index()
        hourly.columns = ["hour", "sessions"]
        peak_hr_val = hourly.loc[hourly["sessions"].idxmax()]

        colors = ["#F97316" if h == peak_hr_val["hour"] else "#7C3AED" for h in hourly["hour"]]
        fig_hour = go.Figure(go.Bar(
            x=hourly["hour"], y=hourly["sessions"],
            marker=dict(color=colors),
        ))
        day_name = pd.Timestamp(sel_date).strftime("%A, %b %d")
        fig_hour.update_layout(
            title=f"⏰ Hourly Logins on {day_name} — peak {int(peak_hr_val['hour'])}:00 ({len(sess_day)} sessions)",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155"), title_font=dict(color="#1E293B", size=13),
            height=380, margin=dict(l=10, r=10, t=50, b=10),
            xaxis=dict(title="Hour (UTC)", dtick=2, gridcolor="rgba(0,0,0,0.06)"),
            yaxis=dict(title="Sessions", gridcolor="rgba(0,0,0,0.06)"),
        )
        st.plotly_chart(fig_hour, width='stretch')
    else:
        st.info(f"No sessions recorded on {sel_date}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 2: Device & Platform Analytics ───────────────────────────────────
st.markdown("### 📲 Device & Platform Analytics")
st.markdown("""<div class="section-desc">
Understanding <strong>which devices, operating systems, and browsers</strong> users prefer is critical for
optimizing the platform experience. A high mobile share suggests the need for mobile-first design and
responsive UI. Browser breakdown helps prioritize compatibility testing — ensuring the top browsers render
the app correctly.
</div>""", unsafe_allow_html=True)

r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    device_counts = sess_all["device"].value_counts().reset_index()
    device_counts.columns = ["device", "count"]

    fig_dev = px.pie(
        device_counts, values="count", names="device",
        title="📲 Mobile vs Desktop Sessions",
        hole=0.5,
        color_discrete_map={"Mobile": "#7C3AED", "Desktop": "#22D3EE", "Unknown": "#94A3B8"},
    )
    fig_dev.update_traces(
        textinfo="label+percent",
        textfont=dict(size=13, color="#FFFFFF", family="Inter"),
        pull=[0.03] * len(device_counts),
    )
    fig_dev.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155", family="Inter"),
        title_font=dict(color="#1E293B", size=15),
        height=400, margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(font=dict(size=10, color="#475569"), bgcolor="rgba(0,0,0,0)"),
        annotations=[dict(
            text=f"<b>{total_sessions:,}</b><br>sessions",
            x=0.5, y=0.5, font=dict(size=13, color="#1E293B"), showarrow=False,
        )],
    )
    st.plotly_chart(fig_dev, width='stretch')

with r2c2:
    os_counts = sess_all["os"].value_counts().reset_index()
    os_counts.columns = ["os", "count"]

    os_colors = {
        "Android": "#7C3AED", "Windows": "#059669", "iOS": "#F97316",
        "Linux": "#DB2777", "macOS": "#0891B2", "Other": "#94A3B8",
    }
    fig_os = go.Figure(go.Bar(
        x=os_counts["os"], y=os_counts["count"],
        marker=dict(color=[os_colors.get(o, "#94A3B8") for o in os_counts["os"]]),
        text=os_counts["count"].apply(lambda x: f"{x:,}"),
        textposition="outside",
        textfont=dict(color="#334155", size=10),
    ))
    fig_os.update_layout(
        title="💻 OS Breakdown",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"), title_font=dict(color="#1E293B", size=15),
        height=400, margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(gridcolor="rgba(0,0,0,0.0)"),
        yaxis=dict(title="Sessions", gridcolor="rgba(0,0,0,0.06)"),
    )
    st.plotly_chart(fig_os, width='stretch')

with r2c3:
    br_counts = sess_all["browser"].value_counts().reset_index()
    br_counts.columns = ["browser", "count"]

    br_colors = {
        "Chrome": "#7C3AED", "Safari": "#059669", "Samsung": "#F97316",
        "Edge": "#2563EB", "Opera": "#DC2626", "Firefox": "#D97706", "Other": "#94A3B8",
    }
    fig_br = go.Figure(go.Bar(
        x=br_counts["browser"], y=br_counts["count"],
        marker=dict(color=[br_colors.get(b, "#94A3B8") for b in br_counts["browser"]]),
        text=br_counts["count"].apply(lambda x: f"{x:,}"),
        textposition="outside",
        textfont=dict(color="#334155", size=10),
    ))
    fig_br.update_layout(
        title="🌐 Browser Breakdown",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"), title_font=dict(color="#1E293B", size=15),
        height=400, margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(gridcolor="rgba(0,0,0,0.0)"),
        yaxis=dict(title="Sessions", gridcolor="rgba(0,0,0,0.06)"),
    )
    st.plotly_chart(fig_br, width='stretch')


st.markdown("<br>", unsafe_allow_html=True)

# ── Section 3: Engagement Patterns ───────────────────────────────────────────
st.markdown("### 📊 Engagement Patterns")
st.markdown("""<div class="section-desc">
The <strong>top users leaderboard</strong> identifies your most active power users who are key to driving
adoption and can serve as brand ambassadors. Understanding <strong>returning vs single-session users</strong>
helps measure user retention and stickiness of the platform.
</div>""", unsafe_allow_html=True)

sessions_per_user = sess_all.groupby("userId").size().reset_index(name="session_count")

r3c1, r3c2 = st.columns(2)

with r3c1:
    top_users = sessions_per_user.sort_values("session_count", ascending=True).tail(15)
    if not user.empty and "id" in user.columns:
        name_map = user.set_index("id")["name"].to_dict() if "name" in user.columns else {}
        top_users = top_users.copy()
        top_users["user_label"] = top_users["userId"].map(
            lambda uid: name_map.get(uid, uid[:12] + "...")
        )
    else:
        top_users = top_users.copy()
        top_users["user_label"] = top_users["userId"].apply(lambda x: x[:12] + "...")

    fig_tu = go.Figure(go.Bar(
        x=top_users["session_count"],
        y=top_users["user_label"],
        orientation="h",
        marker=dict(
            color=top_users["session_count"],
            colorscale=[[0,"#CFFAFE"],[0.4,"#22D3EE"],[1,"#0891B2"]],
            showscale=False,
        ),
        text=top_users["session_count"],
        textposition="outside",
        textfont=dict(color="#334155", size=10),
    ))
    fig_tu.update_layout(
        title="🏆 Top 15 Users by Session Count",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"), title_font=dict(color="#1E293B", size=15),
        height=400, margin=dict(l=10, r=60, t=50, b=10),
        xaxis=dict(title="Sessions", gridcolor="rgba(0,0,0,0.06)"),
        yaxis=dict(tickfont=dict(size=9, color="#475569")),
    )
    st.plotly_chart(fig_tu, width='stretch')

with r3c2:
    # Sessions distribution summary
    single = (sessions_per_user["session_count"] == 1).sum()
    returning = (sessions_per_user["session_count"] > 1).sum()
    return_pct = returning / len(sessions_per_user) * 100 if len(sessions_per_user) > 0 else 0

    fig_ret = px.pie(
        pd.DataFrame({"Type": ["Single Session", "Returning Users"], "Count": [single, returning]}),
        values="Count", names="Type",
        title="🔄 User Retention Overview",
        hole=0.5,
        color_discrete_map={"Returning Users": "#7C3AED", "Single Session": "#E2E8F0"},
    )
    fig_ret.update_traces(
        textinfo="label+percent+value",
        textfont=dict(size=12, family="Inter"),
        pull=[0.03, 0],
    )
    fig_ret.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155", family="Inter"),
        title_font=dict(color="#1E293B", size=15),
        height=400, margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(font=dict(size=10, color="#475569"), bgcolor="rgba(0,0,0,0)"),
        annotations=[dict(
            text=f"<b>{return_pct:.0f}%</b><br>return",
            x=0.5, y=0.5, font=dict(size=14, color="#7C3AED"), showarrow=False,
        )],
    )
    st.plotly_chart(fig_ret, width='stretch')


