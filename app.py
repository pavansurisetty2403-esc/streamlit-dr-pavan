import streamlit as st
from PIL import Image
import time
import os
import requests
from report_utils import run_pipeline

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Diabetic Retinopathy PS",
    page_icon="🩺",
    layout="wide",
)

# ================== MODEL SETUP ==================
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

# ================== STYLES ==================
st.markdown("""
<style>
html, body {
    background-color: #0f1115;
    color: #eaecef;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(12px);}
    to {opacity: 1; transform: translateY(0);}
}

.fade { animation: fadeIn 0.7s ease forwards; }

.card {
    background: linear-gradient(145deg, #161a22, #0d0f14);
    border-radius: 18px;
    padding: 26px;
    margin-bottom: 28px;
    box-shadow: 0 14px 35px rgba(0,0,0,0.6);
}

.center { display: flex; justify-content: center; }

.status { font-size: 34px; font-weight: 700; }
.conf { color: #9aa4b2; }

.success {
    background: linear-gradient(135deg, #143a25, #0f2a1c);
    border-radius: 14px;
    padding: 14px;
    color: #4ade80;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("""
<div class="card fade">
<h1>🩺 Diabetic Retinopathy PS</h1>
<p style="color:#9aa4b2">
AI-assisted diabetic retinopathy screening & automated health reporting
</p>
</div>
""", unsafe_allow_html=True)

# ================== ABOUT DR ==================
st.markdown("""
<div class="card fade">
<h2>About Diabetic Retinopathy</h2>
<p>
Diabetic Retinopathy (DR) is a diabetes-related eye disease caused by damage
to retinal blood vessels. Early detection can prevent irreversible vision loss.
</p>

<h3>Stages</h3>
<ul>
<li>No DR</li>
<li>Mild</li>
<li>Moderate</li>
<li>Severe</li>
<li>Proliferative</li>
</ul>

<h3>What this system does</h3>
<ul>
<li>Preprocesses fundus images</li>
<li>Uses deep learning to assess retinal damage</li>
<li>Predicts DR stage with confidence</li>
<li>Generates a clinical PDF report</li>
</ul>
</div>
""", unsafe_allow_html=True)

# ================== UPLOAD ==================
st.markdown("""
<div class="card fade center">
<h2>Upload Fundus Image</h2>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

# ================== ANALYSIS ==================
if uploaded:
    with st.spinner("Analyzing retinal image…"):
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        image_bytes = uploaded.getvalue()
        model_path = ensure_model()

        cls, prob, pdf_bytes = run_pipeline(image_bytes, model_path)

    # ================== RESULT ==================
    st.markdown(f"""
    <div class="card fade">
        <h2>Retinal Status</h2>
        <div class="status">{cls}</div>
        <div class="conf">Confidence: {prob*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.success("Analysis complete")

    # ================== PDF ==================
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Export Health Report (PDF)",
        data=pdf_bytes,
        file_name="Diabetic_Retinopathy_Report.pdf",
        mime="application/pdf"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="success fade">
    Report generated successfully. You may download and share it with your healthcare provider.
    </div>
    """, unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown("""
<p style="text-align:center; color:#9aa4b2; margin-top:40px">
For screening only. Always consult a certified ophthalmologist.
</p>
""", unsafe_allow_html=True)
