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
/* Apple-style hover glow */
.card,
.info-card {
    transition:
        transform 0.45s cubic-bezier(.2,.8,.2,1),
        box-shadow 0.45s cubic-bezier(.2,.8,.2,1),
        border-color 0.45s ease;
}

.card:hover,
.info-card:hover {
    transform: translateY(-6px);
    box-shadow:
        0 35px 80px rgba(0,0,0,0.55),
        0 0 0 1px rgba(124,245,211,0.12),
        0 0 28px rgba(91,140,255,0.18);
    border-color: rgba(124,245,211,0.25);
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
st.markdown("""
<style>
.section-title {
    font-size: 40px;
    font-weight: 700;
    margin-bottom: 18px;
    background: linear-gradient(90deg, #5b8cff, #7cf5d3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #5b8cff, #7cf5d3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

/* Section snap + reveal + hover lift (FINAL) */
.snap-section {
    scroll-margin-top: 80px;
    border-radius: 32px;

    /* entry animation */
    opacity: 0;
    transform: translateY(60px) scale(0.96);
    animation: snapIn 0.9s cubic-bezier(.2,.8,.2,1) both;

    /* hover behavior */
    transition:
        transform 0.6s cubic-bezier(.2,.8,.2,1),
        box-shadow 0.6s cubic-bezier(.2,.8,.2,1);
}

.snap-section:hover {
    transform: translateY(-4px) scale(1);
    box-shadow:
        0 0 0 1px rgba(124,245,211,0.12),
        0 60px 140px rgba(0,0,0,0.6);
}

@keyframes snapIn {
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}




# ================= ABOUT SECTION STYLES =================
st.markdown("""
<style>
.about-section {
    padding: 64px 56px;
    border-radius: 32px;
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.05),
        rgba(255,255,255,0.015)
    );
    box-shadow: 0 50px 120px rgba(0,0,0,0.6);
    margin: 80px auto;
    max-width: 1100px;
}

.fade-up {
    opacity: 0;
    transform: translateY(24px);
    animation: fadeUp 0.8s ease forwards;
}

.fade-up.delay-1 { animation-delay: 0.2s; }
.fade-up.delay-2 { animation-delay: 0.4s; }
.fade-up.delay-3 { animation-delay: 0.6s; }

@keyframes fadeUp {
    to { opacity: 1; transform: translateY(0); }
}

.info-card {
    margin-top: 28px;
    padding: 26px 28px;
    border-radius: 22px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}

.info-title {
    color: #7cf5d3;
    font-weight: 600;
    margin-bottom: 8px;
}
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
<div class="about-section snap-section">

  <h2 class="section-title fade-up">About Diabetic Retinopathy</h2>

  <p class="fade-up delay-1" style="max-width:900px; color:#cfd5e2; font-size:16px;">
    Diabetic Retinopathy (DR) is a progressive eye disease caused by long-term diabetes.
    Persistently high blood sugar damages the tiny blood vessels of the retina —
    the light-sensitive tissue responsible for vision.
  </p>

  <p class="fade-up delay-2" style="max-width:900px; color:#cfd5e2; font-size:16px;">
    In early stages, DR usually has no symptoms. As damage increases, blood vessels may
    leak fluid, become blocked, or grow abnormally — leading to blurred vision,
    dark spots, and permanent blindness if untreated.
  </p>

  <div class="info-card fade-up delay-1">
    <div class="info-title sub-title">Why it’s dangerous</div>
    <p style="color:#b8bfcc;">
      Vision loss from DR is often irreversible. When symptoms appear,
      significant retinal damage has usually already occurred.
    </p>
  </div>

  <div class="info-card fade-up delay-2">
    <div class="info-title sub-title">Who is at risk</div>
    <p style="color:#b8bfcc;">
      Anyone with diabetes — especially for more than 5–10 years —
      poor glucose control, high blood pressure, kidney disease,
      or smoking history.
    </p>
  </div>

  <div class="info-card fade-up delay-3">
    <div class="info-title sub-title">Why early screening matters</div>
    <p style="color:#b8bfcc;">
      Early screening allows treatment before vision loss begins.
      Regular eye exams can reduce blindness risk by more than 90%.
    </p>
  </div>

</div>
""", unsafe_allow_html=True)


# ================= HOW IT WORKS =================
st.markdown("""
<div class="card fade">
<h2 class="section-title fade-up">How It Works</h2>
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
  <h2 class="section-title fade-up center">Upload Fundus Image</h2>
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
