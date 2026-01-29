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

# ================= MODEL SETUP =================
MODEL_URL = "https://huggingface.co/Pavansetty/DR-Pavan/resolve/main/efficientnet_b3_state_dict.pt"
MODEL_PATH = "efficientnet_b3_state_dict.pt"

@st.cache_resource
def ensure_model():
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Downloading AI model (one-time setup)…"):
            r = requests.get(MODEL_URL)
            r.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                f.write(r.content)
    return MODEL_PATH

# ================= STYLES (ChronoTask inspired) =================
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

.success {
    background: linear-gradient(135deg, rgba(90,255,170,0.18), rgba(60,200,150,0.06));
    border-radius: 18px;
    padding: 16px;
    color: #7cf5d3;
}

button[kind="primary"] {
    background: linear-gradient(135deg, #5b8cff, #7cf5d3);
    color: #0b0d12;
    border-radius: 14px;
    font-weight: 600;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================= HERO =================
st.markdown("""
<div class="hero fade">
  <h1>Diabetic Retinopathy <span class="accent">PS</span></h1>
  <p style="max-width:760px; color:#aab0c0; font-size:16px">
    AI-powered retinal screening platform inspired by modern clinical dashboards.
    Upload a fundus image to receive an automated diabetic retinopathy assessment
    and a downloadable clinical report.
  </p>
</div>
""", unsafe_allow_html=True)

# ================= ABOUT DR =================
st.markdown("""
<div class="card fade">
<h2>About Diabetic Retinopathy</h2>

<p>
<b>Diabetic Retinopathy (DR)</b> is a diabetes-related eye disease caused by progressive
damage to retinal blood vessels. Early stages are often asymptomatic, but advanced
stages can lead to <b>permanent vision loss</b>.
</p>

<h3>Stages</h3>
<ul>
<li>No DR – Healthy retina</li>
<li>Mild – Microaneurysms appear</li>
<li>Moderate – Vessel blockage and leakage</li>
<li>Severe – Retinal ischemia</li>
<li>Proliferative – Abnormal vessel growth (highest risk)</li>
</ul>

<h3>What This Platform Does</h3>
<ul>
<li>Preprocesses and enhances fundus images</li>
<li>Analyzes retinal vascular damage using deep learning</li>
<li>Predicts DR stage with confidence</li>
<li>Generates a detailed patient-friendly PDF report</li>
</ul>

<p style="color:#9aa4b2">
This tool is for screening and educational purposes only and does not replace
professional ophthalmic diagnosis.
</p>
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
      <div class="status">{cls}</div>
      <div class="conf">Confidence: {prob*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.success("Analysis completed successfully")

    # ================= PDF EXPORT =================
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Download Clinical Report (PDF)",
        data=pdf_bytes,
        file_name="Diabetic_Retinopathy_Report.pdf",
        mime="application/pdf"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="success fade">
    Report generated. You may download and share it with a healthcare professional.
    </div>
    """, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("""
<p style="text-align:center; color:#9aa4b2; margin-top:40px">
Always consult a certified ophthalmologist for medical decisions.
</p>
""", unsafe_allow_html=True)
