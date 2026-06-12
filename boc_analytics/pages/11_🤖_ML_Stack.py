"""
pages/11_🤖_ML_Stack.py — ML Algorithms used in this Dashboard
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from shared_styles import inject_shared_styles, inject_sidebar_brand

st.set_page_config(page_title="BOC · ML Stack", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#FFFFFF;color:#1E293B;}
.page-title{font-size:2rem;font-weight:800;color:#1E293B;margin-bottom:0.2rem;}
.page-sub{color:#64748B;font-size:0.95rem;margin-bottom:1.5rem;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F172A,#1E293B) !important;
  border-right:1px solid #334155;}
.ml-block{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:16px;padding:2rem;position:relative;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.06);margin-bottom:1.5rem;transition:transform 0.2s ease,box-shadow 0.2s ease;}
.ml-block:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.1);}
.ml-block-header{display:flex;align-items:center;gap:1rem;margin-bottom:1rem;}
.ml-block-icon{font-size:2.2rem;width:56px;height:56px;display:flex;align-items:center;justify-content:center;border-radius:14px;flex-shrink:0;}
.ml-block-title{font-size:1.25rem;font-weight:800;color:#1E293B;}
.ml-block-badge{display:inline-block;padding:0.2rem 0.7rem;border-radius:20px;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;}
.ml-block-body{font-size:0.92rem;color:#475569;line-height:1.7;}
.ml-block-body b{color:#1E293B;}
.ml-how{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:1rem 1.2rem;margin-top:1rem;font-size:0.85rem;color:#334155;line-height:1.7;}
.ml-how-title{font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#64748B;margin-bottom:0.4rem;}
.ml-used-in{margin-top:0.8rem;font-size:0.82rem;color:#64748B;}
.ml-used-in span{display:inline-block;background:rgba(30,41,59,0.06);border:1px solid #E2E8F0;padding:0.15rem 0.6rem;border-radius:6px;font-size:0.78rem;font-weight:600;color:#1E293B;margin:0.15rem 0.2rem;}
</style>
""", unsafe_allow_html=True)

inject_shared_styles()
inject_sidebar_brand()

st.markdown('<div class="page-title">🤖 ML Stack</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Machine Learning algorithms and AI models used across this dashboard</div>', unsafe_allow_html=True)

st.info("This page explains the **4 core ML/AI techniques** powering the BOC Analytics dashboard — from how we extract data from bill images to how we segment users and detect fraud.")

# ═══════════════════════════════════════════════════════════════════════════════
# 1. K-MEANS CLUSTERING
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="ml-block" style="border-left:4px solid #7C3AED;">'
'<div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#7C3AED,#DB2777);"></div>'
'<div class="ml-block-header">'
'<div class="ml-block-icon" style="background:rgba(124,58,237,0.08);">🎯</div>'
'<div>'
'<div class="ml-block-title">K-Means Clustering</div>'
'<span class="ml-block-badge" style="color:#7C3AED;background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.2);">Unsupervised ML</span>'
'</div>'
'</div>'
'<div class="ml-block-body">'
'K-Means is an <b>unsupervised machine learning algorithm</b> that groups similar users together without needing any pre-labeled data. '
'It works by finding natural "clusters" of users who behave similarly — some spend a lot and come back often (Champions), '
'while others signed up but rarely return (Dormant).'
'<br><br>'
'In this dashboard, each user is represented by <b>3 numbers</b> — their Recency, Frequency, and Monetary scores (see RFM below). '
'K-Means takes these 3 numbers for every user and finds groups where users within the same group are '
'most alike and users across groups are most different.'
'<div class="ml-how">'
'<div class="ml-how-title">⚙️ How it works in our dashboard</div>'
'<b>1.</b> Calculate RFM scores for each user (Recency, Frequency, Monetary)<br>'
'<b>2.</b> Normalize the scores using <b>StandardScaler</b> so no single metric dominates<br>'
'<b>3.</b> Run K-Means with <b>k = 2 to 8 clusters</b> (adjustable via slider)<br>'
'<b>4.</b> Each cluster is auto-labeled based on its average RFM characteristics<br>'
'&nbsp;&nbsp;&nbsp;&nbsp;(e.g., high Frequency + high Monetary = "🏆 Champions")<br>'
'<b>5.</b> Results are visualized as 2D scatter plots (Frequency vs Monetary, Frequency vs Recency)'
'</div>'
'<div class="ml-used-in">'
'📍 Used in: <span>🎯 Customer Segmentation</span> <span>👤 User Profile</span>'
'</div>'
'</div>'
'</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. RFM ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="ml-block" style="border-left:4px solid #0891B2;">'
'<div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#0891B2,#059669);"></div>'
'<div class="ml-block-header">'
'<div class="ml-block-icon" style="background:rgba(8,145,178,0.08);">📊</div>'
'<div>'
'<div class="ml-block-title">RFM Analysis</div>'
'<span class="ml-block-badge" style="color:#0891B2;background:rgba(8,145,178,0.08);border:1px solid rgba(8,145,178,0.2);">Feature Engineering</span>'
'</div>'
'</div>'
'<div class="ml-block-body">'
'RFM stands for <b>Recency, Frequency, and Monetary</b> — three behavioral dimensions that together '
'paint a clear picture of each user\'s engagement level:'
'<br><br>'
'<b>🕐 Recency (R)</b> — How many days since the user last uploaded a bill? Lower is better — a user who uploaded yesterday is more engaged than one from 6 months ago.<br><br>'
'<b>📈 Frequency (F)</b> — How many total bills has the user uploaded in their lifetime? More bills = more active user.<br><br>'
'<b>💰 Monetary (M)</b> — How much has the user spent in total (converted to USD)? Higher spend = higher value customer.'
'<br><br>'
'Each metric is scored <b>1 to 5</b> using quintile binning (dividing users into 5 equal groups). '
'A user scoring <b>R=5, F=5, M=5</b> is a Champion; one scoring <b>R=1, F=1, M=1</b> is Dormant. '
'The RFM scores also serve as the <b>input features for K-Means clustering</b>.'
'<div class="ml-how">'
'<div class="ml-how-title">⚙️ How it works in our dashboard</div>'
'<b>1.</b> For each user, compute: days since last bill, total bill count, total spend (USD)<br>'
'<b>2.</b> Score each metric 1–5 using <b>quintile binning</b> (pd.qcut)<br>'
'<b>3.</b> Sum the three scores → <b>RFM Total</b> (range: 3–15)<br>'
'<b>4.</b> Segment users by rules: 12–15 = Champion, 9–11 = Loyal, 6–8 = At Risk, 3–5 = Dormant<br>'
'<b>5.</b> These same R, F, M values are fed into K-Means for ML-powered segmentation'
'</div>'
'<div class="ml-used-in">'
'📍 Used in: <span>👥 Users</span> <span>🎯 Customer Segmentation</span> <span>👤 User Profile</span>'
'</div>'
'</div>'
'</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 3. GEMINI OCR / LLM EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="ml-block" style="border-left:4px solid #4F46E5;">'
'<div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#4F46E5,#7C3AED);"></div>'
'<div class="ml-block-header">'
'<div class="ml-block-icon" style="background:rgba(79,70,229,0.08);">🔤</div>'
'<div>'
'<div class="ml-block-title">Gemini AI — OCR & Data Extraction</div>'
'<span class="ml-block-badge" style="color:#4F46E5;background:rgba(79,70,229,0.08);border:1px solid rgba(79,70,229,0.2);">LLM / Computer Vision</span>'
'</div>'
'</div>'
'<div class="ml-block-body">'
'Google\'s <b>Gemini</b> is a multimodal Large Language Model (LLM) that can understand both text and images. '
'When a user uploads a photo of their bill or receipt, Gemini acts as an intelligent OCR engine — it doesn\'t '
'just read text, it <b>understands the structure</b> of the document.'
'<br><br>'
'Unlike traditional OCR that simply extracts raw text, Gemini identifies and extracts <b>structured fields</b>: '
'merchant name, individual line items with prices, total amount, tax, currency, invoice date, and spending category. '
'It handles bills in <b>46+ currencies</b> across multiple languages and formats — handwritten receipts, '
'printed invoices, digital bills, and more.'
'<div class="ml-how">'
'<div class="ml-how-title">⚙️ How it works in our dashboard</div>'
'<b>1.</b> User uploads a bill image through the BOC mobile app<br>'
'<b>2.</b> The image is sent to <b>Google Gemini API</b> with a structured extraction prompt<br>'
'<b>3.</b> Gemini returns JSON with: merchant, items[], totalAmount, tax, currency, date, category<br>'
'<b>4.</b> <b>Schema validation</b> ensures all fields match expected formats<br>'
'<b>5.</b> Extracted data is stored in the <b>bill_extraction</b> table — this powers every chart in the dashboard'
'</div>'
'<div class="ml-used-in">'
'📍 Used in: <span>📊 All Dashboard Pages</span> (this is the primary data source)'
'</div>'
'</div>'
'</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 4. TRUTHSCAN — FRAUD DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="ml-block" style="border-left:4px solid #DC2626;">'
'<div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#DC2626,#EA580C);"></div>'
'<div class="ml-block-header">'
'<div class="ml-block-icon" style="background:rgba(220,38,38,0.08);">🛡️</div>'
'<div>'
'<div class="ml-block-title">TruthScan — AI Fraud Detection</div>'
'<span class="ml-block-badge" style="color:#DC2626;background:rgba(220,38,38,0.08);border:1px solid rgba(220,38,38,0.2);">Deep Learning / Computer Vision</span>'
'</div>'
'</div>'
'<div class="ml-block-body">'
'TruthScan is an AI-powered <b>image forensics service</b> that checks whether a bill image is genuine or has been '
'tampered with. It uses deep learning models trained on millions of images to detect three types of manipulation:'
'<br><br>'
'<b>✅ Real</b> — The bill is an authentic, unaltered photograph of a real receipt.<br><br>'
'<b>✏️ Digitally Edited</b> — The image shows signs of digital manipulation — e.g., amounts changed in Photoshop, '
'text overlaid, or parts of the image cloned/spliced.<br><br>'
'<b>🤖 AI Generated</b> — The entire bill image was artificially created using AI tools like '
'Stable Diffusion, Midjourney, or similar generative models.'
'<br><br>'
'Each bill receives a <b>fraud score (0–100)</b> where lower scores indicate authentic bills and higher scores '
'suggest tampering. TruthScan also returns specific <b>fraud flags</b> like "screen recapture detected", '
'"blur anomaly", or "metadata inconsistency".'
'<div class="ml-how">'
'<div class="ml-how-title">⚙️ How it works in our dashboard</div>'
'<b>1.</b> After a bill is uploaded, the image is sent to the <b>TruthScan API</b><br>'
'<b>2.</b> TruthScan\'s CV models analyze pixel patterns, compression artifacts, and metadata<br>'
'<b>3.</b> Returns: <b>score</b> (0–100), <b>finalResult</b> (Real/Edited/AI), and <b>flags[]</b><br>'
'<b>4.</b> Bills are marked as <b>fraud_passed</b> or <b>rejected</b> based on the score threshold<br>'
'<b>5.</b> The Fraud Analysis page visualizes score distributions, flag frequencies, and detection trends'
'</div>'
'<div class="ml-used-in">'
'📍 Used in: <span>🔍 Fraud Analysis</span>'
'</div>'
'</div>'
'</div>', unsafe_allow_html=True)

# ── Summary Box ────────────────────────────────────────────────────────────────
st.markdown('<div style="background:rgba(79,70,229,0.04);border:1px solid rgba(79,70,229,0.15);'
'border-radius:14px;padding:1.5rem 2rem;margin-top:1rem;">'
'<div style="font-size:1rem;font-weight:800;color:#1E293B;margin-bottom:0.8rem;">📋 Summary</div>'
'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;text-align:center;">'
'<div>'
'<div style="font-size:1.8rem;">🎯</div>'
'<div style="font-size:0.82rem;font-weight:700;color:#1E293B;margin-top:0.3rem;">K-Means</div>'
'<div style="font-size:0.75rem;color:#64748B;">User segmentation</div>'
'</div>'
'<div>'
'<div style="font-size:1.8rem;">📊</div>'
'<div style="font-size:0.82rem;font-weight:700;color:#1E293B;margin-top:0.3rem;">RFM Scoring</div>'
'<div style="font-size:0.75rem;color:#64748B;">Behavioral features</div>'
'</div>'
'<div>'
'<div style="font-size:1.8rem;">🔤</div>'
'<div style="font-size:0.82rem;font-weight:700;color:#1E293B;margin-top:0.3rem;">Gemini AI</div>'
'<div style="font-size:0.75rem;color:#64748B;">OCR & extraction</div>'
'</div>'
'<div>'
'<div style="font-size:1.8rem;">🛡️</div>'
'<div style="font-size:0.82rem;font-weight:700;color:#1E293B;margin-top:0.3rem;">TruthScan</div>'
'<div style="font-size:0.75rem;color:#64748B;">Fraud detection</div>'
'</div>'
'</div>'
'</div>', unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 ML Stack")
    st.markdown("---")
    st.markdown("**4 ML Algorithms:**")
    st.markdown("🎯 K-Means Clustering")
    st.markdown("📊 RFM Analysis")
    st.markdown("🔤 Gemini AI (OCR)")
    st.markdown("🛡️ TruthScan (Fraud)")
