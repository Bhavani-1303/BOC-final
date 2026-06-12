"""
pages/7_🎯_Customer_Segmentation.py — Customer Segmentation using RFM and K-Means
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from data_loader import load_all
from shared_styles import inject_shared_styles, inject_sidebar_brand, render_searchable_table

st.set_page_config(page_title="BOC · Customer Segmentation", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#FFFFFF;color:#1E293B;}
.page-title{font-size:2rem;font-weight:800;color:#1E293B;margin-bottom:0.2rem;}
.page-sub{color:#64748B;font-size:0.95rem;margin-bottom:1.5rem;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F172A,#1E293B) !important;
  border-right:1px solid #334155;}
.cluster-card{background:#FFFFFF;
  border:1px solid #E2E8F0;border-radius:12px;padding:1.5rem;
  margin-bottom:1rem;height:100%;box-shadow:0 1px 3px rgba(0,0,0,0.06);}
.cluster-title{font-size:1.1rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;color:#1E293B;}
.stat-row{display:flex;justify-content:space-between;margin-bottom:0.5rem;font-size:0.9rem;}
.stat-label{color:#64748B;}
.stat-value{font-weight:600;color:#1E293B;}
</style>
""", unsafe_allow_html=True)

inject_shared_styles()
inject_sidebar_brand()

dfs = load_all()
bill = dfs.get("bill", pd.DataFrame())
be = dfs.get("bill_extraction", pd.DataFrame())
users = dfs.get("user", pd.DataFrame())

st.markdown('<div class="page-title">🎯 Customer Segmentation</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">RFM Analysis (Recency, Frequency, Monetary) powered by K-Means Clustering</div>', unsafe_allow_html=True)

if bill.empty or be.empty or users.empty:
    st.warning("Not enough data to perform segmentation.")
    st.stop()

# ── Data Preparation (RFM Calculation) ─────────────────────────────────────────

# Merge bill and bill_extraction to get totalAmount for each bill
# De-duplicate: take only the first extraction per bill to avoid inflated counts
be_dedup = be.drop_duplicates(subset=["billId"], keep="first") if "billId" in be.columns else be
merged = bill.merge(be_dedup[["billId", "totalAmount"]], left_on="id", right_on="billId", how="inner", suffixes=("_bill", "_be"))
# Filter out rows with negative or zero amounts just in case
merged = merged[merged["totalAmount"] > 0].copy()

# Determine the "current" date for Recency calculation (max date in dataset)
max_date = merged["createdAt"].max()

# Calculate RFM metrics per user
rfm = merged.groupby("userId").agg(
    LatestDate=("createdAt", "max"),
    Frequency=("id", "nunique"),
    Monetary=("totalAmount", "sum")
).reset_index()

# Calculate Recency in days
rfm["Recency"] = (max_date - rfm["LatestDate"]).dt.days

# Join with user table to get user details
rfm = rfm.merge(users[["id", "name", "email"]], left_on="userId", right_on="id", how="left")
rfm = rfm.dropna(subset=["Recency", "Frequency", "Monetary"])

total_clustered = len(rfm)
total_all_users = len(users)

if total_clustered < 10:
    st.warning("Not enough users with valid transaction history to perform clustering.")
    st.stop()

st.caption(f"ℹ️ Clustering covers **{total_clustered:,}** users with at least 1 completed bill (out of {total_all_users:,} total users). Users with no bills are excluded from RFM analysis.")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Model Parameters")
    n_clusters = st.slider("Number of Clusters (K)", min_value=2, max_value=8, value=4, step=1)
    
    st.markdown("---")
    st.markdown("### 📚 Glossary")
    st.markdown("**Recency**: Days since last bill.")
    st.markdown("**Frequency**: Total number of bills.")
    st.markdown("**Monetary**: Total amount spent.")

# ── K-Means Clustering ─────────────────────────────────────────────────────────
st.info('🤖 **Machine Learning Segmentation** — Users are clustered using K-Means on their RFM scores. Each scatter plot shows how clusters separate across Frequency vs. Monetary and Frequency vs. Recency dimensions. Use the slider to adjust the number of segments.')

# 1. Scale the data
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm[["Recency", "Frequency", "Monetary"]])

# 2. Apply K-Means
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
rfm["Cluster"] = kmeans.fit_predict(rfm_scaled)

# Make Cluster a string for categorical coloring
rfm["Cluster_Label"] = rfm["Cluster"].apply(lambda x: f"Cluster {x}")

# Calculate summary stats for each cluster
cluster_summary = rfm.groupby("Cluster").agg(
    UserCount=("userId", "count"),
    AvgRecency=("Recency", "mean"),
    AvgFrequency=("Frequency", "mean"),
    AvgMonetary=("Monetary", "mean")
).reset_index()

# Sort clusters roughly by value (Monetary & Frequency high, Recency low is better)
# We'll score them simple: M_rank + F_rank - R_rank
cluster_summary["M_Rank"] = cluster_summary["AvgMonetary"].rank()
cluster_summary["F_Rank"] = cluster_summary["AvgFrequency"].rank()
cluster_summary["R_Rank"] = cluster_summary["AvgRecency"].rank(ascending=False) # Lower recency is better
cluster_summary["Score"] = cluster_summary["M_Rank"] + cluster_summary["F_Rank"] + cluster_summary["R_Rank"]

cluster_summary = cluster_summary.sort_values("Score", ascending=False).reset_index(drop=True)

# Assign names based on relative RFM characteristics
mean_recency = cluster_summary["AvgRecency"].mean()
mean_frequency = cluster_summary["AvgFrequency"].mean()
mean_monetary = cluster_summary["AvgMonetary"].mean()

def get_segment_name(row):
    """Assign segment name based on actual cluster RFM characteristics."""
    r = row["AvgRecency"]
    f = row["AvgFrequency"]
    m = row["AvgMonetary"]

    is_recent = r < mean_recency
    is_frequent = f > mean_frequency
    is_high_value = m > mean_monetary

    if is_recent and is_frequent and is_high_value:
        return "👑 Champions"
    elif is_recent and is_frequent:
        return "⭐ Loyal Customers"
    elif is_recent and is_high_value:
        return "💎 Big Spenders"
    elif is_recent:
        return "🌱 Promising"
    elif is_frequent or is_high_value:
        return "⏳ Needs Attention"
    else:
        return "⚠️ At Risk / Dormant"

cluster_summary["SegmentName"] = cluster_summary.apply(get_segment_name, axis=1)

# Now sort by Cluster ID for display
cluster_summary = cluster_summary.sort_values("Cluster", ascending=True).reset_index(drop=True)

# Assign a dynamic color to clusters based on sorted rank for consistent visualization
color_palette = ["#4F46E5", "#059669", "#D97706", "#DC2626", "#0891B2", "#7C3AED", "#DB2777", "#65A30D"]
cluster_colors = {row["Cluster"]: color_palette[i % len(color_palette)] for i, row in cluster_summary.iterrows()}

# ── Segment KPI Cards ──────────────────────────────────────────────────────────
# Build metric cards for each segment, matching the style of other pages
_seg_icons = {"👑 Champions": "👑", "⭐ Loyal Customers": "⭐", "💎 Big Spenders": "💎",
              "🌱 Promising": "🌱", "⏳ Needs Attention": "⏳", "⚠️ At Risk / Dormant": "⚠️"}

seg_html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin-bottom:1.5rem;">'
for _, row in cluster_summary.iterrows():
    seg_name = row["SegmentName"]
    c_id = int(row["Cluster"])
    color = cluster_colors[c_id]
    icon = _seg_icons.get(seg_name, "📊")
    count = int(row["UserCount"])
    # Strip emoji from label for cleaner display
    label = seg_name.split(" ", 1)[1] if " " in seg_name else seg_name
    seg_html += f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;
        padding:1.2rem 1.5rem;position:relative;overflow:hidden;
        box-shadow:0 1px 3px rgba(0,0,0,0.06);">
        <div style="position:absolute;top:0;left:0;right:0;height:4px;background:{color};"></div>
        <div style="font-size:1.5rem">{icon}</div>
        <div style="font-size:1.9rem;font-weight:800;color:#1E293B;">{count:,}</div>
        <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:#000000;font-weight:700;margin-top:2px;">{label}</div>
    </div>"""
seg_html += '</div>'
st.markdown(seg_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Visualizations ─────────────────────────────────────────────────────────────

# --- Row 1: 2D Scatter Plots ---
st.markdown("### 🌌 Customer Segments Analysis")

c1, c2 = st.columns(2)

with c1:
    fig_fm = px.scatter(
        rfm, 
        x="Frequency", 
        y="Monetary", 
        color="Cluster_Label",
        hover_name="name",
        hover_data={"email": True, "Cluster_Label": False, "Recency": True, "Frequency": True, "Monetary": ":.2f"},
        color_discrete_sequence=[cluster_colors[c] for c in sorted(rfm["Cluster"].unique())],
        opacity=0.8,
        log_y=True, # Log scale handles the massive monetary outliers!
        title="Frequency vs Monetary (Log Scale)"
    )
    fig_fm.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#334155"),
        xaxis=dict(gridcolor="rgba(0,0,0,0.06)", title="Frequency (Bills)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.06)", title="Monetary ($)"),
        margin=dict(l=10, r=10, b=10, t=40),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(248,250,252,0.9)",
                    font=dict(color="#1E293B"))
    )
    st.plotly_chart(fig_fm, width='stretch')

with c2:
    fig_rf = px.scatter(
        rfm, 
        x="Recency", 
        y="Frequency", 
        color="Cluster_Label",
        hover_name="name",
        hover_data={"email": True, "Cluster_Label": False, "Recency": True, "Frequency": True, "Monetary": ":.2f"},
        color_discrete_sequence=[cluster_colors[c] for c in sorted(rfm["Cluster"].unique())],
        opacity=0.8,
        title="Recency vs Frequency"
    )
    fig_rf.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#334155"),
        xaxis=dict(gridcolor="rgba(0,0,0,0.06)", title="Recency (Days)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.06)", title="Frequency (Bills)"),
        margin=dict(l=10, r=10, b=10, t=40),
        showlegend=False
    )
    st.plotly_chart(fig_rf, width='stretch')

st.markdown("<br>", unsafe_allow_html=True)

# --- Row 2: Cluster Profiles ---
st.markdown("### 📊 Cluster Profiles")

cols = st.columns(n_clusters)

for i, col in enumerate(cols):
    row = cluster_summary.iloc[i]
    c_id = int(row["Cluster"])
    color = cluster_colors[c_id]
    
    segment_name = row["SegmentName"]
    
    with col:
        st.markdown(f"""
        <div class="cluster-card" style="border-top: 4px solid {color}">
            <div class="cluster-title">
                <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background-color:{color};"></span>
                {segment_name} (Cluster {c_id})
            </div>
            <div class="stat-row">
                <span class="stat-label">Users</span>
                <span class="stat-value">{int(row["UserCount"]):,}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Recency</span>
                <span class="stat-value">{row["AvgRecency"]:.1f} days</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Frequency</span>
                <span class="stat-value">{row["AvgFrequency"]:.1f} bills</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Monetary</span>
                <span class="stat-value">${row["AvgMonetary"]:,.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Row 3: Per-Cluster Spend & Region Analysis ---
st.markdown("### 🔎 Cluster Deep Dive — Spend & Region")
st.info("📊 **Per-Cluster Breakdown** — Select a cluster to see its category spend distribution and geographic footprint. "
        "This helps identify which segments dominate which regions and categories.")

from data_loader import CURRENCY_COUNTRY, CURRENCY_TO_USD

# Enrich: link each clustered user's bills to bill_extraction for category + currency
_user_cluster_map = rfm[["userId", "Cluster", "Cluster_Label"]].copy()
_cluster_bills = merged.merge(_user_cluster_map[["userId", "Cluster", "Cluster_Label"]], on="userId", how="inner")

# Get bill_extraction data for clustered users
_cluster_be = be[be["billId"].isin(_cluster_bills["billId"])].copy()
_cluster_be = _cluster_be.merge(_user_cluster_map[["userId", "Cluster", "Cluster_Label"]],
                                 left_on=_cluster_be["billId"].map(dict(zip(bill["id"], bill["userId"]))),
                                 right_on="userId", how="left")
_cluster_be["country"] = _cluster_be["currency"].map(CURRENCY_COUNTRY).fillna("Other")
_cluster_be["usd_amount"] = _cluster_be.apply(
    lambda r: r["totalAmount"] * CURRENCY_TO_USD.get(r.get("currency", ""), 0)
    if pd.notna(r["totalAmount"]) else 0, axis=1
)

# Cluster selector
_cluster_options = []
for _, row in cluster_summary.iterrows():
    _cluster_options.append(f"{row['SegmentName']} (Cluster {int(row['Cluster'])})")

selected_cluster_label = st.selectbox("Select Cluster to Analyze", _cluster_options, key="cluster_deep")
_sel_cluster_id = int(selected_cluster_label.split("Cluster ")[-1].rstrip(")"))

_sel_be = _cluster_be[_cluster_be["Cluster"] == _sel_cluster_id]
_sel_summary = cluster_summary[cluster_summary["Cluster"] == _sel_cluster_id].iloc[0]
_sel_color = cluster_colors[_sel_cluster_id]

dd1, dd2 = st.columns(2)

with dd1:
    # Category Spend Bar Chart
    if not _sel_be.empty and "category" in _sel_be.columns:
        cat_spend = _sel_be.groupby("category")["usd_amount"].sum().sort_values(ascending=True).tail(10).reset_index()
        cat_spend.columns = ["Category", "Spend (USD)"]

        fig_cat = go.Figure(go.Bar(
            y=cat_spend["Category"],
            x=cat_spend["Spend (USD)"],
            orientation="h",
            marker=dict(
                color=cat_spend["Spend (USD)"],
                colorscale=[[0, "#B0BEC5"], [0.5, _sel_color], [1, _sel_color]],
                showscale=False,
            ),
            text=cat_spend["Spend (USD)"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=10, color="#334155", weight=600),
        ))
        fig_cat.update_layout(
            title=f"🏷️ Category Spend — {_sel_summary['SegmentName']}",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155", family="Inter"),
            title_font=dict(color="#1E293B", size=14),
            height=450, margin=dict(l=10, r=100, t=50, b=10),
            xaxis=dict(title="Spend (USD)", gridcolor="rgba(0,0,0,0.06)"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11, color="#1E293B"),
                       automargin=True),
            showlegend=False,
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No category data for this cluster.")

with dd2:
    # Region Donut Chart
    if not _sel_be.empty and "country" in _sel_be.columns:
        country_dist = _sel_be.groupby("country").agg(
            bill_count=("totalAmount", "count"),
            total_usd=("usd_amount", "sum")
        ).sort_values("bill_count", ascending=False).reset_index()

        # Group small countries as "Others"
        top_countries = country_dist.head(8).copy()
        others_count = country_dist.iloc[8:]["bill_count"].sum() if len(country_dist) > 8 else 0
        if others_count > 0:
            top_countries = pd.concat([top_countries,
                pd.DataFrame([{"country": "Others", "bill_count": others_count, "total_usd": 0}])],
                ignore_index=True)

        fig_region = px.pie(
            top_countries, values="bill_count", names="country",
            hole=0.45,
            color_discrete_sequence=["#546E7A", "#78909C", "#90A4AE", "#B0BEC5",
                                      "#CFD8DC", "#455A64", "#37474F", "#263238", "#ECEFF1"],
        )
        fig_region.update_traces(
            textinfo="percent",
            textposition="inside",
            textfont=dict(size=10, color="#FFFFFF", weight=700),
        )
        fig_region.update_layout(
            title=dict(
                text=f"🌍 Region — {_sel_summary['SegmentName']}",
                font=dict(color="#1E293B", size=13),
                x=0.5, xanchor="center",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155", family="Inter"),
            height=450, margin=dict(l=10, r=10, t=50, b=10),
            legend=dict(
                font=dict(size=9, color="#1E293B"), bgcolor="rgba(0,0,0,0)",
                orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5,
            ),
            annotations=[dict(
                text=f"<b>{int(_sel_summary['UserCount']):,}</b><br>users",
                x=0.5, y=0.5, font=dict(size=13, color="#1E293B"), showarrow=False,
            )],
        )
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info("No region data for this cluster.")

st.markdown("<br>", unsafe_allow_html=True)

# --- Row 4: Full User Segment Table (always visible) ---
st.markdown("### 📋 Full User Segment Data")

display_df = rfm[["name", "email", "Recency", "Frequency", "Monetary", "Cluster_Label"]].copy()
display_df = display_df.rename(columns={"name": "Name", "email": "Email", "Cluster_Label": "Segment"})
display_df["Monetary"] = display_df["Monetary"].apply(lambda x: f"{x:,.2f}")

render_searchable_table(
    display_df,
    search_placeholder="Search by name or email...",
    search_columns=["Name", "Email"],
)

