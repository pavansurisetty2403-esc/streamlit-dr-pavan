import streamlit as st
import time
import os
import requests
from report_utils import run_pipeline

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Diabetic Retinopathy PS",
    page_icon="🩺",
    layout="wide",
)

# ================= MODEL =================
MODEL_URL = "https://huggingface.co/Pavansetty/DR-Pavan/resolve/main/efficientnet_b3_state_dict.pt"
MODEL_PATH = "efficientnet_b3_state_dict.pt"

@st.cache_resource
def ensure_model():
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Downloading AI model (one-time)…"):
            r = requests.get(MODEL_URL)
            r.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                f.write(r.content)
    return MODEL_PATH

# ================= STYLES =================
st.markdown("""
<style>
html, body {
    background: radial-gradient(1200px at 10% 10%, #1a1f2b, #0b0d12);
    color: #e6e9ef;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

.fade { animation: fadeUp 0.7s cubic-bezier(.2,.8,.2,1) forwards; }

.hero {
    padding: 52px 44px;
    border-radius: 28px;
    background:
      linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0)),
      radial-gradient(800px at 0% 0%, rgba(90,140,255,0.22), transparent 60%);
    box-shadow: 0 40px 80px rgba(0,0,0,0.6);
    margin-bottom: 36px;
}

.card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 24px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 30px 60px rgba(0,0,0,0.45);
}

.accent {
    background: linear-gradient(90deg, #5b8cff, #7cf5d3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.center { display: flex; justify-content: center; }

.status {
    font-size: 38px;
    font-weight: 700;
    margin-top: 8px;
}

.conf { color: #9aa4b2; margin-top: 6px; }

/* confidence bar */
.conf-bar {
    height: 8px;
    border-radius: 6px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
    margin-top: 12px;
}
.conf-fill {
    height: 100%;
    background: linear-gradient(90deg, #5b8cff, #7cf5d3);
    width: 0%;
    animation: fillBar 1.2s ease forwards;
}
@keyframes fillBar {
    to { width: var(--w); }
}

/* badge pulse */
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(124,245,211,0.15);
    color: #7cf5d3;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(124,245,211,0.4); }
    70% { box-shadow: 0 0 0 12px rgba(124,245,211,0); }
    100% { box-shadow: 0 0 0 0 rgba(124,245,211,0); }
}

/* timeline */
.timeline {
    border-left: 2px solid rgba(255,255,255,0.1);
    padding-left: 20px;
}
.timeline-item {
    margin-bottom: 18px;
    position: relative;
}
.timeline-item::before {
    content: "";
    position: absolute;
    left: -11px;
    top: 6px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: linear-gradient(135deg, #5b8cff, #7cf5d3);
}

.success {
    background: linear-gradient(135deg, rgba(90,255,170,0.18), rgba(60,200,150,0.06));
    border-radius: 18px;
    padding: 16px;
    color: #7cf5d3;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================= HERO =================
st.markdown("""
<div class="hero fade">
  <h1>Diabetic Retinopathy <span class="accent">PS</span></h1>
  <p style="max-width:760px; color:#aab0c0; font-size:16px">
    AI-powered retinal screening that detects diabetic retinopathy early,
    explains disease severity, and generates clinical reports in seconds.
  </p>
</div>
""", unsafe_allow_html=True)

# ================= ABOUT =================
st.markdown("""
<div class="card fade">
<h2>About Diabetic Retinopathy</h2>
<p>
Diabetic Retinopathy is a diabetes-related eye disease caused by damage to retinal
blood vessels. It often progresses silently and may cause permanent vision loss
if untreated.
</p>
</div>
""", unsafe_allow_html=True)

# ================= HOW IT WORKS =================
st.markdown("""
<div class="card fade">
<h2>How It Works</h2>
<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px">
<div><b>1. Upload</b><br><span class="conf">Secure fundus image upload</span></div>
<div><b>2. Analyze</b><br><span class="conf">Deep learning retinal assessment</span></div>
<div><b>3. Report</b><br><span class="conf">Stage prediction & PDF</span></div>
</div>
</div>
""", unsafe_allow_html=True)

# ================= UPLOAD =================
st.markdown("""
<div class="card fade center">
  <h2 class="accent">Upload Fundus Image</h2>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

# ================= ANALYSIS =================
if uploaded:
    with st.spinner("Running retinal analysis…"):
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.008)
            progress.progress(i + 1)

        image_bytes = uploaded.getvalue()
        model_path = ensure_model()
        cls, prob, pdf_bytes = run_pipeline(image_bytes, model_path)

    # ================= RESULT =================
    st.markdown(f"""
    <div class="card fade">
      <h3 class="accent">Retinal Status</h3>
      <span class="badge">{cls}</span>
      <div class="status">{cls}</div>
      <div class="conf-bar">
        <div class="conf-fill" style="--w:{prob*100:.1f}%"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ================= STAGES =================
    st.markdown("""
    <div class="card fade">
    <h2>Stages of Diabetic Retinopathy</h2>
    <div class="timeline">
      <div class="timeline-item">No DR – Healthy retina</div>
      <div class="timeline-item">Mild – Microaneurysms</div>
      <div class="timeline-item">Moderate – Leakage & blockage</div>
      <div class="timeline-item">Severe – Ischemia</div>
      <div class="timeline-item">Proliferative – Abnormal vessels</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # ================= PDF =================
    st.download_button(
        "⬇️ Download Clinical Report (PDF)",
        pdf_bytes,
        file_name="Diabetic_Retinopathy_Report.pdf",
        mime="application/pdf"
    )

    st.markdown("""
    <div class="success fade">
    ✅ Report generated successfully and ready for download
    </div>
    """, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("""
<p style="text-align:center; color:#9aa4b2; margin-top:40px">
Always consult a certified ophthalmologist.
</p>
""", unsafe_allow_html=True)
