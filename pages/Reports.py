import streamlit as st
import time
import os
import requests
from report_utils import run_pipeline

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Reports | Diabetic Retinopathy PS",
    layout="wide",
)

# ================= AUTH =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.switch_page("Login.py")
    st.stop()

# ================= HIDE STREAMLIT DEFAULT NAV =================
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("""
    <style>
    .sidebar-container {
        display:flex;
        flex-direction:column;
        gap:18px;
        padding-top:10px;
    }

    .brand {
        font-size:28px;
        font-weight:900;
        background:linear-gradient(90deg,#5b8cff,#7cf5d3);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin-bottom:4px;
    }

    .brand-sub {
        font-size:13px;
        color:#aab2d8;
        margin-bottom:26px;
    }

    .section-title {
        font-size:26px;
        font-weight:900;
        background:linear-gradient(90deg,#6ea8ff,#7cf5d3);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin:22px 0 10px 0;
        letter-spacing:1px;
    }

    div[role="radiogroup"] label {
        font-size:18px !important;
        margin-bottom:8px;
    }

    .account-email {
        font-size:14px;
        color:#8bdcff;
        margin-bottom:12px;
    }

    .button {
        height:52px !important;
        font-size:18px !important;
        border-radius:14px !important;
        border:2px solid #5b8cff !important;
        background:transparent !important;
        color:#e6ebff !important;
    }

    .button:hover {
        background:#5b8cff !important;
        color:#0b0d12 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-container">', unsafe_allow_html=True)

    st.markdown('<div class="brand">Diabetic Retinopathy PS</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Clinical AI Screening</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "",
        ["About DR", "Reports", "History"],
        index=1,
        label_visibility="collapsed"
    )

    if page == "About DR":
        st.switch_page("pages/About_DR.py")
    elif page == "History":
        st.switch_page("pages/History.py")

    st.markdown('<div class="section-title">Account</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="account-email">{st.session_state.get("user_email","")}</div>',
        unsafe_allow_html=True
    )

    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("pages/Login.py")


    st.markdown('</div>', unsafe_allow_html=True)

# ================= GLOBAL THEME =================
st.markdown("""
<style>
html, body {
    background: radial-gradient(1200px at 10% 10%, #1a1f2b, #0b0d12);
    color:#e6e9ef;
    font-family:-apple-system,BlinkMacSystemFont,"Inter",sans-serif;
}

.card {
    background:rgba(255,255,255,0.04);
    border-radius:28px;
    padding:44px;
    box-shadow:0 40px 90px rgba(0,0,0,.55);
    margin-bottom:40px;
}

@keyframes pulseGlow {
    0% { box-shadow:0 0 0 rgba(124,245,211,0); }
    50% { box-shadow:0 0 36px rgba(124,245,211,.35); }
    100% { box-shadow:0 0 0 rgba(124,245,211,0); }
}

.pulse {
    animation:pulseGlow 3.5s ease-in-out infinite;
}

h1 {
    font-size:44px;
    background:linear-gradient(90deg,#5b8cff,#7cf5d3);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
</style>
""", unsafe_allow_html=True)

# ================= HERO =================
st.markdown("""
<div class="card">
  <h1>Upload Fundus Image</h1>
  <p style="color:#aab0c0;font-size:16px">
    Upload a retinal fundus image to generate an AI-powered
    diabetic retinopathy clinical report.
  </p>
</div>
""", unsafe_allow_html=True)

# ================= FILE UPLOAD =================
uploaded = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

# ================= MODEL =================
MODEL_URL = "https://huggingface.co/Pavansetty/DR-Pavan/resolve/main/efficientnet_b3_state_dict.pt"
MODEL_PATH = "efficientnet_b3_state_dict.pt"

@st.cache_resource
def ensure_model():
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Downloading AI model (one-time)…"):
            r = requests.get(MODEL_URL, timeout=30)
            r.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                f.write(r.content)
    return MODEL_PATH

# ================= ANALYSIS =================
if uploaded is not None:
    with st.spinner("Analyzing retinal image…"):
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        model_path = ensure_model()
        cls, prob, pdf_bytes = run_pipeline(uploaded.getvalue(), model_path)

    st.session_state.setdefault("upload_history", []).append({
        "filename": uploaded.name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "result": cls,
        "confidence": f"{prob*100:.2f}%"
    })

    st.markdown(f"""
    <div class="card pulse">
      <h2>{cls}</h2>
      <p style="color:#9aa4b2">Confidence: {prob*100:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

    st.download_button(
        "⬇️ Generate Clinical Report (PDF)",
        pdf_bytes,
        file_name="Diabetic_Retinopathy_Report.pdf",
        mime="application/pdf"
    )
