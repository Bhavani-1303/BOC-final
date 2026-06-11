"""
pages/7_🔍_Fraud_Analysis.py — Fraud Detection & Bill Failure Analysis
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
from collections import Counter
from data_loader import load_all
from shared_styles import inject_shared_styles, inject_sidebar_brand

st.set_page_config(page_title="BOC · Fraud Analysis", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#FFFFFF;color:#1E293B;}
.page-title{font-size:2rem;font-weight:800;color:#1E293B;margin-bottom:0.2rem;}
.page-sub{color:#64748B;font-size:0.95rem;margin-bottom:1.5rem;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F172A,#1E293B) !important;
  border-right:1px solid #334155;}
</style>
""", unsafe_allow_html=True)

inject_shared_styles()
inject_sidebar_brand()

dfs = load_all()
bill = dfs.get("bill", pd.DataFrame())
fc = dfs.get("fraud_check", pd.DataFrame())

st.markdown('<div class="page-title">🔍 Fraud Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Fraud detection scores, decision breakdowns, and bill failure reason analysis</div>', unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────────────────────
fraud_total = len(fc)
fraud_passed = int(fc["decision"].isin(["pass", "fraud_passed"]).sum()) if "decision" in fc.columns and fraud_total else 0
fraud_rejected = fraud_total - fraud_passed
fraud_pass_rate = (fraud_passed / fraud_total * 100) if fraud_total > 0 else 0

# Bill failure stats
total_bills = len(bill)
failed_bills = int((bill["status"] == "extraction_failed").sum()) if "status" in bill.columns else 0
duplicate_bills = int((bill["status"] == "duplicate").sum()) if "status" in bill.columns else 0
completed_bills = int((bill["status"] == "completed").sum()) if "status" in bill.columns else 0
failure_rate = (failed_bills / total_bills * 100) if total_bills > 0 else 0

kpi_data = [
    ("🛡️", f"{fraud_total:,}", "Fraud Checks"),
    ("✅", f"{fraud_passed:,}", "Passed"),
    ("❌", f"{fraud_rejected:,}", "Rejected"),
    ("📊", f"{fraud_pass_rate:.1f}%", "Pass Rate"),
]

kpi_html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;margin-bottom:1.5rem;">'
for icon, val, lbl in kpi_data:
    kpi_html += f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;
        padding:1.2rem 1.5rem;position:relative;overflow:hidden;
        box-shadow:0 1px 3px rgba(0,0,0,0.06);">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#CBD5E1,#1E293B);"></div>
        <div style="font-size:1.4rem">{icon}</div>
        <div style="font-size:1.9rem;font-weight:800;color:#1E293B;">{val}</div>
        <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:#000000;font-weight:700;margin-top:2px;">{lbl}</div>
    </div>"""
kpi_html += '</div>'
st.markdown(kpi_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Fraud Detection
# ══════════════════════════════════════════════════════════════════════════════

if fraud_total > 0 and "decision" in fc.columns:
    # ── Fraud Score Distributions ─────────────────────────────────────────────
    if "score" in fc.columns and "finalResult" in fc.columns:
        st.info("📊 **Fraud Score — Combined Distributions** — These histograms show how fraud scores are distributed across all bills and broken down by detection result. Lower scores indicate authentic bills; higher scores suggest AI-generated or digitally edited content.")

        fc_real = fc[fc["finalResult"] == "Real"]
        fc_edited = fc[fc["finalResult"] == "Digitally Edited"]
        fc_ai = fc[fc["finalResult"] == "AI Generated"]

        # Row: All Bills + Real
        r2c1, r2c2 = st.columns(2)

        with r2c1:
            fig_all = go.Figure(go.Histogram(
                x=fc["score"].dropna(), nbinsx=50,
                marker=dict(color="#EF4444", line=dict(width=0.3, color="#FFFFFF")),
            ))
            fig_all.update_layout(
                title=f"All Bills  (n={fraud_total:,})",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155", family="Inter"),
                title_font=dict(color="#1E293B", size=14),
                height=320, margin=dict(l=10, r=10, t=45, b=10),
                xaxis=dict(title="Fraud score", range=[0, 100], gridcolor="rgba(0,0,0,0.06)"),
                yaxis=dict(title="Bills", gridcolor="rgba(0,0,0,0.06)"),
            )
            st.plotly_chart(fig_all, width='stretch')

        with r2c2:
            fig_real = go.Figure(go.Histogram(
                x=fc_real["score"].dropna(), nbinsx=50,
                marker=dict(color="#10B981", line=dict(width=0.3, color="#FFFFFF")),
            ))
            fig_real.update_layout(
                title=f"Real  (n={len(fc_real):,})",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155", family="Inter"),
                title_font=dict(color="#1E293B", size=14),
                height=320, margin=dict(l=10, r=10, t=45, b=10),
                xaxis=dict(title="Fraud score", range=[0, 100], gridcolor="rgba(0,0,0,0.06)"),
                yaxis=dict(title="Bills", gridcolor="rgba(0,0,0,0.06)"),
            )
            st.plotly_chart(fig_real, width='stretch')

        # Row: Digitally Edited + AI Generated + Detection Result Donut
        r3c1, r3c2, r3c3 = st.columns(3)

        with r3c1:
            fig_edited = go.Figure(go.Histogram(
                x=fc_edited["score"].dropna(), nbinsx=50,
                marker=dict(color="#F59E0B", line=dict(width=0.3, color="#FFFFFF")),
            ))
            fig_edited.update_layout(
                title=f"Digitally Edited  (n={len(fc_edited):,})",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155", family="Inter"),
                title_font=dict(color="#1E293B", size=13),
                height=320, margin=dict(l=10, r=10, t=45, b=10),
                xaxis=dict(title="Fraud score", range=[0, 100], gridcolor="rgba(0,0,0,0.06)"),
                yaxis=dict(title="Bills", gridcolor="rgba(0,0,0,0.06)"),
            )
            st.plotly_chart(fig_edited, width='stretch')

        with r3c2:
            fig_ai = go.Figure(go.Histogram(
                x=fc_ai["score"].dropna(), nbinsx=50,
                marker=dict(color="#EF4444", line=dict(width=0.3, color="#FFFFFF")),
            ))
            fig_ai.update_layout(
                title=f"AI Generated  (n={len(fc_ai):,})",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155", family="Inter"),
                title_font=dict(color="#1E293B", size=13),
                height=320, margin=dict(l=10, r=10, t=45, b=10),
                xaxis=dict(title="Fraud score", range=[0, 100], gridcolor="rgba(0,0,0,0.06)"),
                yaxis=dict(title="Bills", gridcolor="rgba(0,0,0,0.06)"),
            )
            st.plotly_chart(fig_ai, width='stretch')

        with r3c3:
            result_counts = fc["finalResult"].value_counts().reset_index()
            result_counts.columns = ["result", "count"]
            result_color_map = {"Real": "#10B981", "Digitally Edited": "#F59E0B", "AI Generated": "#EF4444"}

            fig_result = px.pie(
                result_counts, values="count", names="result",
                title=f"🔬 Detection Result  ·  {fraud_total:,}",
                hole=0.55,
                color="result",
                color_discrete_map=result_color_map,
            )
            fig_result.update_traces(
                textinfo="percent+value",
                textfont=dict(size=10, color="#334155", family="Inter"),
                pull=[0.03] * len(result_counts),
            )
            real_pct = len(fc_real) / fraud_total * 100 if fraud_total > 0 else 0
            fig_result.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155", family="Inter"),
                title_font=dict(color="#1E293B", size=13),
                height=320, margin=dict(l=10, r=10, t=45, b=10),
                legend=dict(
                    font=dict(size=9, color="#1E293B"),
                    bgcolor="rgba(0,0,0,0)",
                    orientation="h", x=0.0, y=-0.12,
                ),
                annotations=[dict(
                    text=f"<b>{real_pct:.0f}%</b><br>Real",
                    x=0.5, y=0.5,
                    font=dict(size=14, color="#10B981"),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig_result, width='stretch')

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Fraud Flags ───────────────────────────────────────────────────────────
    if "flags" in fc.columns and fc["flags"].notna().sum() > 0:
        st.info("🚩 **Fraud Flags** — Common warning signals detected during fraud analysis. These flags highlight patterns like screen recapture, blur detection, and other anomalies found in bill images.")

        all_flags = []
        for f_val in fc["flags"].dropna():
            try:
                parsed = json.loads(f_val) if isinstance(f_val, str) else f_val
                if isinstance(parsed, list):
                    all_flags.extend([str(x) for x in parsed])
                elif isinstance(parsed, dict):
                    all_flags.extend(parsed.keys())
            except Exception:
                pass
        if all_flags:
            flag_counts = Counter(all_flags)
            flag_df = pd.DataFrame(flag_counts.most_common(15), columns=["flag", "count"])
            fig = px.bar(
                flag_df, x="count", y="flag", orientation="h",
                title="🚩 Most Common Fraud Flags",
                color="count",
                color_continuous_scale=["#FEE2E2", "#F87171", "#DC2626"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155"), title_font=dict(color="#1E293B", size=13),
                height=350, margin=dict(l=10, r=10, t=50, b=10),
                xaxis=dict(gridcolor="rgba(0,0,0,0.06)"),
                yaxis=dict(gridcolor="rgba(0,0,0,0.0)", tickfont=dict(color="#1E293B")),
                coloraxis_showscale=False, showlegend=False,
            )
            st.plotly_chart(fig, width='stretch')

else:
    st.warning("No fraud check data available.")

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Bill Failure Reason Analysis
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<div style="font-size:1.5rem;font-weight:800;color:#1E293B;margin-bottom:0.5rem;">📋 Bill Failure Reason Analysis</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#64748B;font-size:0.9rem;margin-bottom:1rem;">Deep dive into why bills fail — extraction errors, duplicate submissions, and other processing issues</div>', unsafe_allow_html=True)

if "failureReason" in bill.columns:
    fr_df = bill[bill["failureReason"].notna()].copy()
    fr_total = len(fr_df)

    if fr_total > 0:
        # Categorize failure reasons
        def categorize_failure(reason):
            if pd.isna(reason):
                return "Unknown"
            r = str(reason).lower()
            if "older than" in r or "3 months" in r:
                return "Invoice Too Old (>3 months)"
            elif "does not appear to be a bill" in r or "not a bill" in r:
                return "Not a Bill/Receipt"
            elif "date could not be extracted" in r or "date" in r and "extract" in r:
                return "Date Extraction Failed"
            elif "duplicate invoice" in r:
                return "Duplicate Invoice"
            elif "duplicate file" in r:
                return "Duplicate File"
            elif "ocr" in r or "extraction" in r or "parse" in r:
                return "OCR/Extraction Error"
            else:
                return "Other"

        fr_df["failure_category"] = fr_df["failureReason"].apply(categorize_failure)

        # KPI cards for failure analysis
        cat_counts = fr_df["failure_category"].value_counts()
        old_invoices = int(cat_counts.get("Invoice Too Old (>3 months)", 0))
        not_bills = int(cat_counts.get("Not a Bill/Receipt", 0))
        date_failed = int(cat_counts.get("Date Extraction Failed", 0))
        dup_invoices = int(cat_counts.get("Duplicate Invoice", 0))
        dup_files = int(cat_counts.get("Duplicate File", 0))

        fail_kpi_data = [
            ("📅", f"{old_invoices:,}", "Invoice Too Old"),
            ("🚫", f"{not_bills:,}", "Not a Bill"),
            ("📆", f"{date_failed:,}", "Date Failed"),
            ("🔁", f"{dup_invoices:,}", "Duplicate Invoice"),
            ("📄", f"{dup_files:,}", "Duplicate File"),
        ]

        fkpi_html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;margin-bottom:1.5rem;">'
        fail_colors = ["#D97706", "#DC2626", "#7C3AED", "#0891B2", "#64748B"]
        for (icon, val, lbl), color in zip(fail_kpi_data, fail_colors):
            fkpi_html += f"""
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;
                padding:1.2rem 1.5rem;position:relative;overflow:hidden;
                box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                <div style="position:absolute;top:0;left:0;right:0;height:4px;background:{color};"></div>
                <div style="font-size:1.4rem">{icon}</div>
                <div style="font-size:1.9rem;font-weight:800;color:#1E293B;">{val}</div>
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:#000000;font-weight:700;margin-top:2px;">{lbl}</div>
            </div>"""
        fkpi_html += '</div>'
        st.markdown(fkpi_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📊 **Failure Breakdown** — The donut chart shows the distribution of failure categories, while the bar chart displays failure trends over time. Understanding these patterns helps identify systemic issues and improve bill processing quality.")

        # Row 1: Failure Category Donut + Failure over Time
        fc1, fc2 = st.columns(2)

        with fc1:
            cat_df = fr_df["failure_category"].value_counts().reset_index()
            cat_df.columns = ["category", "count"]
            cat_color_map = {
                "Invoice Too Old (>3 months)": "#D97706",
                "Not a Bill/Receipt": "#DC2626",
                "Date Extraction Failed": "#7C3AED",
                "Duplicate Invoice": "#0891B2",
                "Duplicate File": "#64748B",
                "OCR/Extraction Error": "#DB2777",
                "Other": "#1E293B",
            }
            fig = px.pie(
                cat_df, values="count", names="category",
                title=f"📊 Failure Categories  ·  {fr_total:,} failed bills",
                hole=0.55,
                color="category",
                color_discrete_map=cat_color_map,
            )
            fig.update_traces(
                textinfo="percent+value",
                textfont=dict(size=10, color="#334155", family="Inter"),
                pull=[0.03] * len(cat_df),
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155", family="Inter"),
                title_font=dict(color="#1E293B", size=14),
                height=420, margin=dict(l=10, r=10, t=55, b=20),
                legend=dict(
                    font=dict(size=9, color="#1E293B"),
                    bgcolor="rgba(248,250,252,0.8)",
                    bordercolor="#E2E8F0",
                    borderwidth=1,
                    orientation="h", x=0.0, y=-0.15,
                ),
                annotations=[dict(
                    text=f"<b>{fr_total:,}</b><br>Failed",
                    x=0.5, y=0.5,
                    font=dict(size=15, color="#DC2626"),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig, use_container_width=True)

        with fc2:
            # Failures over time — monthly trend
            if "createdAt" in fr_df.columns:
                fr_ts = fr_df.dropna(subset=["createdAt"]).copy()
                fr_ts["month"] = fr_ts["createdAt"].dt.to_period("M").dt.to_timestamp()
                monthly_fail = fr_ts.groupby("month").size().reset_index(name="count")

                fig = go.Figure(go.Bar(
                    x=monthly_fail["month"].dt.strftime("%b %Y"),
                    y=monthly_fail["count"],
                    marker=dict(
                        color=monthly_fail["count"],
                        colorscale=[[0, "#FEE2E2"], [0.4, "#F87171"], [1, "#DC2626"]],
                        showscale=False,
                        line=dict(width=0),
                    ),
                    text=monthly_fail["count"],
                    textposition="outside",
                    textfont=dict(size=11, color="#334155"),
                ))
                fig.update_layout(
                    title=f"📅 Monthly Bill Failures  ·  {fr_total:,} total",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#334155", family="Inter"),
                    title_font=dict(color="#1E293B", size=14),
                    height=420, margin=dict(l=10, r=10, t=55, b=10),
                    xaxis=dict(gridcolor="rgba(0,0,0,0.06)", tickangle=-30, tickfont=dict(size=10)),
                    yaxis=dict(title="Failed Bills", gridcolor="rgba(0,0,0,0.06)"),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row 2: Top Failure Reasons
        st.info("🔬 **Detailed Failure Analysis** — The horizontal bar chart ranks the most common specific failure messages.")

        with st.container():
            def clean_failure_reason(reason):
                if pd.isna(reason):
                    return "Unknown"
                r = str(reason)
                if "Duplicate invoice" in r:
                    return "Duplicate invoice (content match)"
                elif "Duplicate file" in r:
                    return "Duplicate file (hash match)"
                elif "RESOURCE_EXHAUSTED" in r:
                    return "Gemini API: Resource exhausted"
                elif "INVALID_ARGUMENT" in r:
                    return "Gemini API: Invalid argument"
                elif "Truthscan" in r and "timed out" in r:
                    return "Truthscan: Polling timed out"
                elif "Unable to process input image" in r:
                    return "Gemini: Unable to process image"
                elif "Schema validation failed" in r and "currency" in r:
                    return "Schema: Invalid currency format"
                elif "Schema validation failed" in r and "items" in r:
                    return "Schema: Items array is null"
                elif "Schema validation failed" in r:
                    return "Schema validation failed"
                if len(r) > 55:
                    return r[:52] + "..."
                return r

            fr_df["clean_reason"] = fr_df["failureReason"].apply(clean_failure_reason)
            reason_counts = fr_df["clean_reason"].value_counts().head(10).reset_index()
            reason_counts.columns = ["reason", "count"]
            reason_counts = reason_counts.sort_values("count", ascending=True)

            COLORS = ["#4F46E5", "#D97706", "#059669", "#DC2626", "#0891B2",
                       "#DB2777", "#65A30D", "#EA580C", "#2563EB", "#10B981"]
            bar_colors = [COLORS[i % len(COLORS)] for i in range(len(reason_counts))]

            fig = go.Figure(go.Bar(
                x=reason_counts["count"],
                y=reason_counts["reason"],
                orientation="h",
                marker=dict(color=bar_colors, line=dict(width=0)),
                text=reason_counts["count"].apply(lambda v: f"{v:,}"),
                textposition="outside",
                textfont=dict(size=11, color="#334155"),
            ))
            fig.update_layout(
                title="🏆 Top Failure Reasons",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155", family="Inter"),
                title_font=dict(color="#1E293B", size=14),
                height=480, margin=dict(l=10, r=80, t=55, b=10),
                xaxis=dict(title="Number of Bills", gridcolor="rgba(0,0,0,0.06)"),
                yaxis=dict(
                    gridcolor="rgba(0,0,0,0.0)",
                    tickfont=dict(color="#1E293B", size=11),
                    automargin=True,
                ),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)


        st.markdown("<br>", unsafe_allow_html=True)

        # Row 3: Failure Rate by Bill Status + Repeat Offender Analysis
        st.info("👥 **User Impact Analysis** — Identify which users submit the most failed bills and understand the relationship between bill status and failure patterns.")

        fc5, fc6 = st.columns(2)

        with fc5:
            # Top users with most failures
            if "userId" in fr_df.columns:
                user_fail = fr_df.groupby("userId").agg(
                    fail_count=("id", "count"),
                ).reset_index().sort_values("fail_count", ascending=False).head(10)

                # Join with user table for names
                users = dfs.get("user", pd.DataFrame())
                if not users.empty:
                    user_fail = user_fail.merge(users[["id", "name"]], left_on="userId", right_on="id", how="left")
                    user_fail["label"] = user_fail["name"].fillna(user_fail["userId"].str[:12] + "...")
                else:
                    user_fail["label"] = user_fail["userId"].str[:12] + "..."

                user_fail = user_fail.sort_values("fail_count", ascending=True)

                fig = go.Figure(go.Bar(
                    x=user_fail["fail_count"],
                    y=user_fail["label"],
                    orientation="h",
                    marker=dict(
                        color=user_fail["fail_count"],
                        colorscale=[[0, "#DBEAFE"], [0.4, "#60A5FA"], [1, "#2563EB"]],
                        showscale=False,
                        line=dict(width=0),
                    ),
                    text=user_fail["fail_count"].apply(lambda v: f"{v:,} fails"),
                    textposition="outside",
                    textfont=dict(size=10, color="#334155"),
                ))
                fig.update_layout(
                    title="👥 Users with Most Failures",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#334155", family="Inter"),
                    title_font=dict(color="#1E293B", size=14),
                    height=420, margin=dict(l=10, r=80, t=55, b=10),
                    xaxis=dict(title="Failed Bills", gridcolor="rgba(0,0,0,0.06)"),
                    yaxis=dict(gridcolor="rgba(0,0,0,0.0)", tickfont=dict(color="#1E293B", size=10)),
                    showlegend=False,
                )
                st.plotly_chart(fig, width='stretch')

        with fc6:
            # Failure category vs bill status
            if "status" in fr_df.columns:
                status_cat = fr_df.groupby(["status", "failure_category"]).size().reset_index(name="count")
                cat_order = ["Invoice Too Old (>3 months)", "Not a Bill/Receipt", "Date Extraction Failed",
                             "Duplicate Invoice", "Duplicate File", "OCR/Extraction Error", "Other"]
                cat_colors_map = dict(zip(cat_order, ["#D97706", "#DC2626", "#7C3AED", "#0891B2", "#64748B", "#DB2777", "#1E293B"]))

                fig = px.bar(
                    status_cat, x="status", y="count", color="failure_category",
                    title="📊 Failure Categories by Bill Status",
                    color_discrete_map=cat_colors_map,
                    barmode="stack",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#334155", family="Inter"),
                    title_font=dict(color="#1E293B", size=14),
                    height=420, margin=dict(l=10, r=10, t=55, b=10),
                    xaxis=dict(title="Bill Status", gridcolor="rgba(0,0,0,0.06)", tickfont=dict(size=10)),
                    yaxis=dict(title="Count", gridcolor="rgba(0,0,0,0.06)"),
                    legend=dict(
                        font=dict(size=8, color="#1E293B"),
                        bgcolor="rgba(248,250,252,0.8)",
                        orientation="h", x=0.0, y=-0.25,
                    ),
                )
                st.plotly_chart(fig, width='stretch')

    else:
        st.info("No failure reason data available in the bill table.")
else:
    st.info("No failureReason column found in the bill data.")

# ── Sidebar Summary ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Fraud Summary")
    st.markdown("---")
    if fraud_total > 0:
        st.markdown(f"**Fraud checks:** {fraud_total:,}")
        st.markdown(f"**Pass rate:** {fraud_pass_rate:.1f}%")
        st.markdown(f"**Rejected:** {fraud_rejected:,}")
    st.markdown("---")
    st.markdown(f"**Total bills:** {total_bills:,}")
    st.markdown(f"**Failed:** {failed_bills:,}")
    st.markdown(f"**Duplicates:** {duplicate_bills:,}")
    st.markdown(f"**Failure rate:** {failure_rate:.1f}%")
