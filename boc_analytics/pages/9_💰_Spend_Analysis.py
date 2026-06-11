"""
pages/8_💰_Spend_Analysis.py — Spend Analysis
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all, CURRENCY_TO_USD
from shared_styles import inject_shared_styles, inject_sidebar_brand

st.set_page_config(page_title="BOC · Spend Analysis", page_icon="💰", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#FFFFFF;color:#1E293B;}
.page-title{font-size:2rem;font-weight:800;color:#1E293B;margin-bottom:0.2rem;}
.page-sub{color:#64748B;font-size:0.95rem;margin-bottom:1.5rem;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F172A,#1E293B) !important;
  border-right:1px solid #334155;}

/* KPI Cards */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg,#CBD5E1,#1E293B);
}
.kpi-val { font-size: 1.5rem; font-weight: 800; color: #1E293B; }
.kpi-lbl { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #1E293B; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

inject_shared_styles()
inject_sidebar_brand()

dfs = load_all()
be = dfs.get("bill_extraction", pd.DataFrame())

st.markdown('<div class="page-title">💰 Spend Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">A detailed, easy-to-understand breakdown of your spending habits across categories and merchants.</div>', unsafe_allow_html=True)

if be.empty:
    st.warning("No bill extraction data found.")
    st.stop()

# Data Prep
opt_df = be.dropna(subset=["category", "totalAmount", "merchantName"]).copy()
opt_df = opt_df[opt_df["totalAmount"] > 0]
opt_df = opt_df[opt_df["totalAmount"] < opt_df["totalAmount"].quantile(0.99)] # Remove massive anomalies

with st.sidebar:
    st.markdown("### 🔽 Filter by Currency")
    currencies = sorted(opt_df["currency"].dropna().unique().tolist())
    default_curr = "USD" if "USD" in currencies else (currencies[0] if currencies else None)
    selected_curr = st.selectbox("Select Currency", currencies, index=currencies.index(default_curr) if default_curr in currencies else 0)

df_curr = opt_df[opt_df["currency"] == selected_curr].copy()

if df_curr.empty:
    st.info(f"No data for {selected_curr}.")
    st.stop()

# Basic Metrics
total_spend = df_curr["totalAmount"].sum()
tx_count = len(df_curr)
avg_spend = total_spend / tx_count if tx_count > 0 else 0



# ── Category Analysis ────────────────────────────────────────────────────────
st.markdown("### 🏷️ Category-Wise Spend Analysis")
st.info('Understanding **what** you spend your money on is the first step to optimization. The chart below shows your total spending divided into distinct categories. Look for large bars in categories like "Food", "Entertainment", or "Shopping" to identify where you can easily cut back.')

cat_spend = df_curr.groupby("category")["totalAmount"].sum().reset_index().sort_values("totalAmount", ascending=True)
# Calculate percentages for explainability
cat_spend["Percentage"] = (cat_spend["totalAmount"] / total_spend) * 100

fig_cat = px.bar(
    cat_spend, 
    x="totalAmount", 
    y="category", 
    orientation="h",
    title="Total Spend per Category",
    color="totalAmount",
    color_continuous_scale="Teal",
    labels={"totalAmount": f"Amount ({selected_curr})", "category": "Category"}
)
fig_cat.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#334155"),
    xaxis=dict(gridcolor="rgba(0,0,0,0.06)"), yaxis=dict(title="", tickfont=dict(color="#1E293B")), coloraxis_showscale=False
)
st.plotly_chart(fig_cat, width='stretch')

st.markdown("<br>", unsafe_allow_html=True)

# ── Merchant Spend Analytics ──────────────────────────────────────────────────
st.markdown("### 💰 Merchant Spend Analytics")
st.info("📊 **Spend Intelligence** — Understand how spending is distributed across merchants and countries. All amounts are converted to USD for fair comparison across currencies.")

# Prepare spend data with USD conversion (filter outliers at 99th percentile)
spend_df = opt_df.dropna(subset=["totalAmount","currency"]).copy()
spend_df = spend_df[spend_df["totalAmount"] > 0]
spend_df = spend_df[spend_df["totalAmount"] < spend_df["totalAmount"].quantile(0.99)]
spend_df["usd_amount"] = spend_df.apply(
    lambda r: r["totalAmount"] * CURRENCY_TO_USD.get(r["currency"], 0), axis=1
)

CURRENCY_TO_COUNTRY = {
    "IDR": "Indonesia", "INR": "India", "NGN": "Nigeria", "VND": "Vietnam", "PHP": "Philippines",
    "USD": "United States", "DZD": "Algeria", "PKR": "Pakistan", "TRY": "Turkey", "UAH": "Ukraine",
    "IRR": "Iran", "BDT": "Bangladesh", "GBP": "United Kingdom", "MYR": "Malaysia", "EUR": "Europe",
    "HKD": "Hong Kong", "MMK": "Myanmar", "BRL": "Brazil", "AED": "UAE", "CHF": "Switzerland",
    "ZAR": "South Africa", "ETB": "Ethiopia", "TWD": "Taiwan", "KES": "Kenya", "EGP": "Egypt",
    "THB": "Thailand", "JPY": "Japan", "UZS": "Uzbekistan", "XOF": "West Africa", "KHR": "Cambodia",
    "NPR": "Nepal", "CAD": "Canada", "RUB": "Russia", "MXN": "Mexico", "SGD": "Singapore",
    "PEN": "Peru", "AUD": "Australia", "PLN": "Poland", "NZD": "New Zealand", "MAD": "Morocco",
    "LKR": "Sri Lanka", "KRW": "South Korea", "CNY": "China", "SAR": "Saudi Arabia", "SEK": "Sweden",
    "CRC": "Costa Rica", "ISK": "Iceland", "KWD": "Kuwait", "LYD": "Libya", "SYP": "Syria",
    "TND": "Tunisia", "ZMW": "Zambia", "UGX": "Uganda", "XAF": "Central Africa", "AZN": "Azerbaijan",
}
spend_df["country"] = spend_df["currency"].map(CURRENCY_TO_COUNTRY).fillna("Other")

sa1, sa2 = st.columns(2)

with sa1:
    merch_spend = spend_df.groupby("merchantName").agg(
        usd_total=("usd_amount", "sum"),
        bill_count=("totalAmount", "count"),
    ).reset_index()
    merch_spend = merch_spend.sort_values("usd_total", ascending=True).tail(15)

    fig_ms = go.Figure(go.Bar(
        x=merch_spend["usd_total"],
        y=merch_spend["merchantName"],
        orientation="h",
        marker=dict(
            color=merch_spend["usd_total"],
            colorscale=[[0,"#D1FAE5"],[0.3,"#34D399"],[0.7,"#059669"],[1,"#064E3B"]],
            showscale=False,
        ),
        text=merch_spend.apply(lambda r: f"${r['usd_total']:,.0f}  ({int(r['bill_count'])} bills)", axis=1),
        textposition="outside",
        textfont=dict(color="#334155", size=9),
    ))
    fig_ms.update_layout(
        title="💰 Top 15 Merchants by Spend (USD)",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"), title_font=dict(color="#1E293B", size=15),
        height=500, margin=dict(l=10, r=140, t=50, b=10),
        xaxis=dict(title="Total Spend (USD)", gridcolor="rgba(0,0,0,0.06)"),
        yaxis=dict(tickfont=dict(size=9, color="#1E293B")),
    )
    st.plotly_chart(fig_ms, width='stretch')

with sa2:
    country_spend = spend_df.groupby("country").agg(
        usd_total=("usd_amount", "sum"),
        bill_count=("totalAmount", "count"),
    ).reset_index().sort_values("usd_total", ascending=True).tail(20)

    fig_cs = go.Figure(go.Bar(
        x=country_spend["usd_total"],
        y=country_spend["country"],
        orientation="h",
        marker=dict(
            color=country_spend["usd_total"],
            colorscale=[[0,"#DBEAFE"],[0.3,"#60A5FA"],[0.7,"#2563EB"],[1,"#1E3A8A"]],
            showscale=False,
        ),
        text=country_spend.apply(lambda r: f"${r['usd_total']:,.0f}  ({int(r['bill_count'])} bills)", axis=1),
        textposition="outside",
        textfont=dict(color="#334155", size=9),
    ))
    fig_cs.update_layout(
        title="🌍 Top 20 Countries by Spend (USD)",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"), title_font=dict(color="#1E293B", size=15),
        height=560, margin=dict(l=10, r=140, t=50, b=10),
        xaxis=dict(title="Total Spend (USD)", gridcolor="rgba(0,0,0,0.06)"),
        yaxis=dict(tickfont=dict(size=10, color="#1E293B")),
    )
    st.plotly_chart(fig_cs, width='stretch')

st.markdown("<br>", unsafe_allow_html=True)

# ── Tax Spend Analytics ───────────────────────────────────────────────────────
st.markdown("### 🧾 Tax Spend Analytics")

tax_df = spend_df[spend_df["taxAmount"].notna() & (spend_df["taxAmount"] > 0)].copy()
tax_df["tax_usd"] = tax_df.apply(
    lambda r: r["taxAmount"] * CURRENCY_TO_USD.get(r["currency"], 0), axis=1
)

if len(tax_df) > 0:
    tx1, tx2 = st.columns(2)

    with tx1:
        tax_by_country = tax_df.groupby("country").agg(
            tax_total_usd=("tax_usd", "sum"),
            bill_count=("taxAmount", "count"),
        ).reset_index().sort_values("tax_total_usd", ascending=True).tail(20)

        fig_tc = go.Figure(go.Bar(
            x=tax_by_country["tax_total_usd"],
            y=tax_by_country["country"],
            orientation="h",
            marker=dict(
                color=tax_by_country["tax_total_usd"],
                colorscale=[[0,"#FEF3C7"],[0.3,"#FBBF24"],[0.7,"#D97706"],[1,"#92400E"]],
                showscale=False,
            ),
            text=tax_by_country["tax_total_usd"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
            textfont=dict(color="#334155", size=9),
        ))
        fig_tc.update_layout(
            title="🌍 Tax Collected by Country (USD)",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155"), title_font=dict(color="#1E293B", size=15),
            height=420, margin=dict(l=10, r=90, t=50, b=10),
            xaxis=dict(title="Total Tax (USD)", gridcolor="rgba(0,0,0,0.06)"),
            yaxis=dict(tickfont=dict(size=10, color="#1E293B")),
        )
        st.plotly_chart(fig_tc, width='stretch')

    with tx2:
        tax_by_merch = tax_df.groupby("merchantName").agg(
            tax_total_usd=("tax_usd", "sum"),
            bill_count=("taxAmount", "count"),
        ).reset_index().sort_values("tax_total_usd", ascending=True).tail(12)

        fig_tm = go.Figure(go.Bar(
            x=tax_by_merch["tax_total_usd"],
            y=tax_by_merch["merchantName"],
            orientation="h",
            marker=dict(
                color=tax_by_merch["tax_total_usd"],
                colorscale=[[0,"#FCE7F3"],[0.3,"#F472B6"],[0.7,"#DB2777"],[1,"#831843"]],
                showscale=False,
            ),
            text=tax_by_merch["tax_total_usd"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
            textfont=dict(color="#334155", size=9),
        ))
        fig_tm.update_layout(
            title="🏪 Tax by Top Merchants (USD)",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155"), title_font=dict(color="#1E293B", size=15),
            height=420, margin=dict(l=10, r=90, t=50, b=10),
            xaxis=dict(title="Total Tax (USD)", gridcolor="rgba(0,0,0,0.06)"),
            yaxis=dict(tickfont=dict(size=9, color="#1E293B")),
        )
        st.plotly_chart(fig_tm, width='stretch')




else:
    st.info("No tax data available.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Spending Heatmaps ────────────────────────────────────────────────────────
st.markdown("### 🗓️ Spending Heatmaps")
st.info("📊 **Activity Patterns** — These heatmaps reveal when and where spending happens most. "
        "Darker cells indicate higher activity. Hover over any cell for exact values.")

import numpy as np

# Prepare heatmap data
heat_df = opt_df.dropna(subset=["createdAt", "totalAmount"]).copy()
heat_df["createdAt"] = pd.to_datetime(heat_df["createdAt"], errors="coerce")
heat_df = heat_df.dropna(subset=["createdAt"])
heat_df["day_of_week"] = heat_df["createdAt"].dt.day_name()
heat_df["hour"] = heat_df["createdAt"].dt.hour
heat_df["usd_amount"] = heat_df.apply(
    lambda r: r["totalAmount"] * CURRENCY_TO_USD.get(r.get("currency", ""), 0), axis=1
)

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ── Heatmap 1: Bill Activity — Day × Hour (full width, annotated) ────────────
pivot_count = heat_df.groupby(["day_of_week", "hour"]).size().reset_index(name="bill_count")
pivot_table = pivot_count.pivot(index="day_of_week", columns="hour", values="bill_count").fillna(0)
pivot_table = pivot_table.reindex(day_order).fillna(0)
# Ensure all 24 hours
for h in range(24):
    if h not in pivot_table.columns:
        pivot_table[h] = 0
pivot_table = pivot_table[sorted(pivot_table.columns)]

z_vals = pivot_table.values.astype(int)
x_labels = [f"{h}:00" for h in range(24)]
y_labels = day_short

# Create annotation text
annotations = []
for i in range(len(y_labels)):
    for j in range(len(x_labels)):
        val = int(z_vals[i][j])
        # Choose text color based on intensity
        max_val = z_vals.max()
        text_color = "#FFFFFF" if val > max_val * 0.5 else "#1E293B"
        annotations.append(dict(
            x=x_labels[j], y=y_labels[i],
            text=str(val) if val > 0 else "",
            font=dict(size=9, color=text_color, family="Inter"),
            showarrow=False, xref="x", yref="y",
        ))

fig_hm1 = go.Figure(data=go.Heatmap(
    z=z_vals,
    x=x_labels,
    y=y_labels,
    colorscale=[
        [0, "#EEF2FF"],
        [0.15, "#C7D2FE"],
        [0.3, "#A5B4FC"],
        [0.5, "#818CF8"],
        [0.7, "#6366F1"],
        [0.85, "#4F46E5"],
        [1, "#3730A3"],
    ],
    xgap=3, ygap=3,
    hovertemplate="<b>%{y}</b> at <b>%{x}</b><br>Bills: %{z:,}<extra></extra>",
    showscale=True,
    colorbar=dict(
        title=dict(text="Bills", font=dict(size=11, color="#64748B")),
        tickfont=dict(size=10, color="#64748B"),
        thickness=14, len=0.9,
        outlinewidth=0,
    ),
))
fig_hm1.update_layout(
    title=dict(text="🕐 Bill Submission Activity — Day × Hour", font=dict(size=16, color="#1E293B")),
    annotations=annotations,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#334155", family="Inter"),
    height=340, margin=dict(l=10, r=10, t=50, b=40),
    xaxis=dict(
        title="Hour of Day", tickfont=dict(size=10, color="#64748B"),
        side="bottom", dtick=1,
    ),
    yaxis=dict(
        title="", tickfont=dict(size=12, color="#1E293B", weight=600),
        autorange="reversed",
    ),
)
st.plotly_chart(fig_hm1, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Heatmap 2: Category × Day — Spend (USD) with annotations ─────────────────
cat_day = heat_df.dropna(subset=["category"]).groupby(["category", "day_of_week"])["usd_amount"].sum().reset_index()
pivot_cat = cat_day.pivot(index="category", columns="day_of_week", values="usd_amount").fillna(0)
pivot_cat = pivot_cat.reindex(columns=day_order).fillna(0)
pivot_cat["_total"] = pivot_cat.sum(axis=1)
pivot_cat = pivot_cat.sort_values("_total", ascending=False).drop(columns=["_total"])

z_cat = pivot_cat.values
# Normalize per row for better color distribution
z_norm = np.zeros_like(z_cat)
for i in range(z_cat.shape[0]):
    row_max = z_cat[i].max()
    z_norm[i] = z_cat[i] / row_max if row_max > 0 else 0

# Annotations with dollar values
cat_annotations = []
for i, cat in enumerate(pivot_cat.index):
    for j, day in enumerate(day_short):
        val = z_cat[i][j]
        intensity = z_norm[i][j]
        text_color = "#FFFFFF" if intensity > 0.55 else "#334155"
        if val >= 1000:
            txt = f"${val/1000:.1f}k"
        elif val > 0:
            txt = f"${val:.0f}"
        else:
            txt = ""
        cat_annotations.append(dict(
            x=day, y=cat, text=txt,
            font=dict(size=10, color=text_color, family="Inter"),
            showarrow=False, xref="x", yref="y",
        ))

fig_hm2 = go.Figure(data=go.Heatmap(
    z=z_norm,
    x=day_short,
    y=list(pivot_cat.index),
    customdata=z_cat,
    colorscale=[
        [0, "#ECFDF5"],
        [0.2, "#A7F3D0"],
        [0.4, "#6EE7B7"],
        [0.6, "#34D399"],
        [0.8, "#059669"],
        [1, "#064E3B"],
    ],
    xgap=4, ygap=4,
    hovertemplate="<b>%{y}</b> on <b>%{x}</b><br>Spend: $%{customdata:,.0f}<extra></extra>",
    showscale=False,
))
fig_hm2.update_layout(
    title=dict(text="📦 Category × Day of Week Spend (USD)", font=dict(size=16, color="#1E293B")),
    annotations=cat_annotations,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#334155", family="Inter"),
    height=450, margin=dict(l=10, r=10, t=50, b=10),
    xaxis=dict(tickfont=dict(size=13, color="#1E293B", weight=600), side="bottom"),
    yaxis=dict(tickfont=dict(size=12, color="#1E293B"), autorange="reversed"),
)
st.plotly_chart(fig_hm2, use_container_width=True)
