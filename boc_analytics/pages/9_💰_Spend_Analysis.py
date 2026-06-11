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
st.markdown("### 🌍 Country × Category Spend Heatmap")
st.info("📊 **Geographic Spend Patterns** — This heatmap shows how spending is distributed "
        "across countries and categories. Darker cells indicate higher spend. Hover over any cell for exact USD values.")

import numpy as np


# ── Heatmap 2: Country × Category — Spend (USD) ──────────────────────────────
from data_loader import CURRENCY_COUNTRY

# Use ALL bill_extraction data (not currency-filtered) for country heatmap
be_all = dfs.get("bill_extraction", pd.DataFrame()).copy()
be_all = be_all.dropna(subset=["totalAmount", "currency", "category"])
be_all = be_all[be_all["totalAmount"] > 0]
be_all["country"] = be_all["currency"].map(CURRENCY_COUNTRY).fillna("Other")
be_all["usd_amount"] = be_all.apply(
    lambda r: r["totalAmount"] * CURRENCY_TO_USD.get(r["currency"], 0), axis=1
)

# Get top 12 countries by total USD spend
country_totals = be_all.groupby("country")["usd_amount"].sum().sort_values(ascending=False)
top_countries = country_totals.head(12).index.tolist()

# Get top categories
cat_totals = be_all.groupby("category")["usd_amount"].sum().sort_values(ascending=False)
top_cats = cat_totals.index.tolist()

# Build pivot
cc_df = be_all[be_all["country"].isin(top_countries)]
cc_agg = cc_df.groupby(["country", "category"])["usd_amount"].sum().reset_index()
pivot_cc = cc_agg.pivot(index="country", columns="category", values="usd_amount").fillna(0)
pivot_cc = pivot_cc.reindex(columns=top_cats).fillna(0)
pivot_cc["_total"] = pivot_cc.sum(axis=1)
pivot_cc = pivot_cc.sort_values("_total", ascending=False).drop(columns=["_total"])

z_cc = pivot_cc.values

# Normalize per row
z_cc_norm = np.zeros_like(z_cc)
for i in range(z_cc.shape[0]):
    row_max = z_cc[i].max()
    z_cc_norm[i] = z_cc[i] / row_max if row_max > 0 else 0

# Annotations
cc_annotations = []
for i, country in enumerate(pivot_cc.index):
    for j, cat in enumerate(pivot_cc.columns):
        val = z_cc[i][j]
        intensity = z_cc_norm[i][j]
        text_color = "#FFFFFF" if intensity > 0.55 else "#334155"
        if val >= 1_000_000:
            txt = f"${val/1_000_000:.1f}M"
        elif val >= 1000:
            txt = f"${val/1000:.1f}k"
        elif val > 0:
            txt = f"${val:.0f}"
        else:
            txt = ""
        cc_annotations.append(dict(
            x=cat, y=country, text=txt,
            font=dict(size=9, color=text_color, family="Inter"),
            showarrow=False, xref="x", yref="y",
        ))

fig_cc = go.Figure(data=go.Heatmap(
    z=z_cc_norm,
    x=list(pivot_cc.columns),
    y=list(pivot_cc.index),
    customdata=z_cc,
    colorscale=[
        [0, "#EFF6FF"],
        [0.2, "#BFDBFE"],
        [0.4, "#60A5FA"],
        [0.6, "#3B82F6"],
        [0.8, "#1D4ED8"],
        [1, "#1E3A5F"],
    ],
    xgap=4, ygap=4,
    hovertemplate="<b>%{y}</b> — <b>%{x}</b><br>Spend: $%{customdata:,.0f}<extra></extra>",
    showscale=False,
))
fig_cc.update_layout(
    title=dict(text="🌍 Country × Category Spend (USD)", font=dict(size=16, color="#1E293B")),
    annotations=cc_annotations,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#334155", family="Inter"),
    height=500, margin=dict(l=10, r=10, t=50, b=10),
    xaxis=dict(tickfont=dict(size=11, color="#1E293B", weight=600), side="bottom", tickangle=-30),
    yaxis=dict(tickfont=dict(size=12, color="#1E293B", weight=600), autorange="reversed"),
)
st.plotly_chart(fig_cc, use_container_width=True)

