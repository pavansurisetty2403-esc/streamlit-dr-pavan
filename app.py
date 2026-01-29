import streamlit as st
import requests
import os
from report_utils import (
    run_pipeline,
    DR_EXPLANATION,
    DR_ADVICE,
    DR_RISK_FACTORS,
    DR_RECOMMENDED_TESTS
)

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Retinal Health",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# APPLE HEALTH DARK MODE + ANIMATIONS
# =========================================================
st.markdown("""
<style>
/* ===== Base ===== */
.stApp {
    background-color: #0b0d12;
    color: #e5e7eb;
}

.block-container {
    padding: 2rem;
}

/* ===== Cards ===== */
.apple-card {
    background: #16181d;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}

/* ===== Typography ===== */
.apple-title {
    font-size: 30px;
    font-weight: 600;
    color: #f9fafb;
}

.apple-subtitle {
    font-size: 15px;
    color: #9ca3af;
}

.metric-value {
    font-size: 34px;
    font-weight: 600;
    color: #f9fafb;
}

/* ===== Accent bar ===== */
.accent {
    width: 6px;
    height: 100%;
    border-radius: 4px;
    margin-right: 14px;
}

/* ===== Buttons ===== */
.stDownloadButton button {
    background: linear-gradient(180deg, #1f2937, #0f172a);
    color: #f9fafb;
    border-radius: 16px;
    height: 56px;
    font-size: 16px;
    border: none;
}

.stDownloadButton button:hover {
    background: #1e40af;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background-color: #0f1117;
}

/* ===== Inputs ===== */
input, textarea {
    background-color: #0f1117 !important;
    color: #f9fafb !important;
    border-radius: 10px !important;
    border: 1px solid #272a33 !important;
}

/* ===== Expanders ===== */
details summary {
    color: #f9fafb !important;
    font-weight: 500;
}

details p {
    color: #d1d5db !important;
}

/* ===== Animations ===== */
.fade-in {
    animation: fadeIn 0.8s ease-out forwards;
    opacity: 0;
}

.slide-up {
    animation: slideUp 0.9s ease-out forwards;
    opacity: 0;
    transform: translateY(12px);
}

@keyframes fadeIn {
    to { opacity: 1; }
}

@keyframes slideUp {
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="apple-card fade-in">
  <div class="apple-title">Retinal Health</div>
  <div class="apple-subtitle">
    AI-assisted diabetic retinopathy screening & reporting
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR — PATIENT INFO
# =========================================================
st.sidebar.header("Patient Information (optional)")
patient_name = st.sidebar.text_input("Patient name")
patient_age = st.sidebar.number_input("Age", min_value=0, max_value=120)
patient_id = st.sidebar.text_input("Patient ID")

# =========================================================
# ENSURE MODEL FILE
# =========================================================
@st.cache_resource
def ensure_model_file():
    model_path = "efficientnet_b3_state_dict.pt"
    if not os.path.exists(model_path):
        url = "https://huggingface.co/Pavansetty/DR-Pavan/resolve/main/efficientnet_b3_state_dict.pt"
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(model_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return model_path

# =========================================================
# MAIN LAYOUT
# =========================================================
left, right = st.columns([1.1, 1])

with left:
    st.markdown("""
    <div class="apple-card slide-up">
      <h3>Upload Fundus Image</h3>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    if uploaded:
        st.image(uploaded, use_column_width=True)

# =========================================================
# RUN ANALYSIS
# =========================================================
if uploaded:
    model_path = ensure_model_file()

    progress = st.progress(0)
    status = st.empty()

    status.info("Preparing image…")
    progress.progress(25)

    with st.spinner("Running retinal analysis…"):
        progress.progress(50)
        cls, prob, pdf_bytes = run_pipeline(
            image_bytes=uploaded.read(),
            model_path=model_path
        )
        progress.progress(100)

    status.success("Analysis complete")

    STAGE_LABELS = {
        0: "No Retinopathy",
        1: "Mild",
        2: "Moderate",
        3: "Severe",
        4: "Proliferative"
    }

    COLORS = ["#22c55e", "#eab308", "#fb923c", "#f97316", "#ef4444"]

    with right:
        st.markdown(f"""
        <div class="apple-card slide-up" style="display:flex; align-items:center;">
            <div class="accent" style="background:{COLORS[cls]};"></div>
            <div>
                <div class="apple-subtitle">Retinal Status</div>
                <div class="metric-value">{STAGE_LABELS[cls]}</div>
                <div class="apple-subtitle">Confidence · {prob*100:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # MEDICAL DETAILS
    # =====================================================
    st.markdown('<div class="apple-card fade-in">', unsafe_allow_html=True)

    with st.expander("About this result"):
        st.markdown(f"<p>{DR_EXPLANATION[cls]}</p>", unsafe_allow_html=True)

    with st.expander("What you should do"):
        st.markdown(f"<p>{DR_ADVICE[cls]}</p>", unsafe_allow_html=True)

    with st.expander("Risk factors"):
        st.markdown(f"<p>{DR_RISK_FACTORS[cls]}</p>", unsafe_allow_html=True)

    with st.expander("Recommended tests"):
        st.markdown(f"<p>{DR_RECOMMENDED_TESTS[cls]}</p>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # EDUCATIONAL CONTENT
    # =====================================================
    st.markdown("""
    <div class="apple-card fade-in">
    <h2>About Diabetic Retinopathy</h2>
    <p>
    Diabetic Retinopathy (DR) is a diabetes-related eye disease caused by damage to
    the retinal blood vessels. It progresses silently in early stages and may lead
    to irreversible vision loss if not detected early.
    </p>

    <h3>Stages of DR</h3>
    <ul>
      <li><b>No DR</b> – Healthy retina</li>
      <li><b>Mild</b> – Microaneurysms appear</li>
      <li><b>Moderate</b> – Increased leakage and blockage</li>
      <li><b>Severe</b> – Large retinal ischemia</li>
      <li><b>Proliferative</b> – Abnormal vessel growth (high risk)</li>
    </ul>

    <h3>What This Website Does</h3>
    <p>
    This platform uses a deep learning model trained on retinal images to assist
    early screening of diabetic retinopathy. It enhances the image, analyzes
    retinal patterns, predicts disease stage, and generates a detailed PDF report
    for patient awareness and follow-up.
    </p>

    <p style="color:#9ca3af; font-size:14px;">
    This tool is for screening and educational purposes only and does not replace
    professional ophthalmic diagnosis.
    </p>
    </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # PDF DOWNLOAD
    # =====================================================
    st.markdown('<div class="apple-card slide-up">', unsafe_allow_html=True)
    st.download_button(
        "Export Health Report (PDF)",
        data=pdf_bytes,
        file_name="Retinal_Health_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================
st.caption(
    "For screening and educational use only. "
    "Always consult a certified ophthalmologist."
)
