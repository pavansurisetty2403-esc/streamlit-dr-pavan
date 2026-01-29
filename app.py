import streamlit as st
from PIL import Image
import tempfile
import time
from report_utils import run_pipeline

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Diabetic Retinopathy PS",
    page_icon="🩺",
    layout="wide",
)

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

.fade {
    animation: fadeIn 0.7s ease forwards;
}

.card {
    background: linear-gradient(145deg, #161a22, #0d0f14);
    border-radius: 18px;
    padding: 26px;
    margin-bottom: 28px;
    box-shadow: 0 14px 35px rgba(0,0,0,0.6);
}

.center {
    display: flex;
    justify-content: center;
}

.status {
    font-size: 34px;
    font-weight: 700;
}

.conf {
    color: #9aa4b2;
}

.success {
    background: linear-gradient(135deg, #143a25, #0f2a1c);
    border-radius: 14px;
    padding: 14px;
    color: #4ade80;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("""
<div class="card fade">
<h1>🩺 Diabetic Retinopathy PS</h1>
<p style="color:#9aa4b2">
AI-assisted retinal screening, disease staging & automated health reporting
</p>
</div>
""", unsafe_allow_html=True)

# ================== ABOUT DR ==================
st.markdown("""
<div class="card fade">
<h2>About Diabetic Retinopathy</h2>

<p>
<b>Diabetic Retinopathy (DR)</b> is a diabetes-related eye disease caused by long-term damage
to the tiny blood vessels of the retina. It often progresses silently and can lead to
<b>irreversible vision loss or blindness</b> if not detected early.
</p>

<h3>Stages of Diabetic Retinopathy</h3>
<ul>
<li><b>No DR</b> – Healthy retina, no visible damage</li>
<li><b>Mild</b> – Small microaneurysms appear</li>
<li><b>Moderate</b> – Increased vessel blockage and leakage</li>
<li><b>Severe</b> – Large retinal ischemia (oxygen deprivation)</li>
<li><b>Proliferative</b> – Abnormal blood vessel growth (high risk of vision loss)</li>
</ul>

<h3>What This Website Does</h3>
<p>
This platform uses a <b>deep learning model trained on retinal fundus images</b> to assist
in early screening of diabetic retinopathy.
</p>

<ul>
<li>Enhances and preprocesses retinal images</li>
<li>Analyzes retinal vascular patterns</li>
<li>Predicts DR stage with confidence score</li>
<li>Generates a detailed, patient-friendly PDF report</li>
</ul>

<p style="color:#9aa4b2">
This tool is intended for screening and educational use only and does not replace
professional ophthalmic diagnosis.
</p>
</div>
""", unsafe_allow_html=True)

# ================== UPLOAD SECTION ==================
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
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded Fundus Image", use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.spinner("Analyzing retinal image…"):
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            image.save(tmp.name)
            cls, prob, pdf_bytes = run_pipeline(tmp.name)

    # ================== RESULT ==================
    st.markdown(f"""
    <div class="card fade">
        <h2>Retinal Status</h2>
        <div class="status">{cls}</div>
        <div class="conf">Confidence: {prob*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.success("Analysis complete")

    # ================== EXPORT ==================
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
For screening and educational use only. Always consult a certified ophthalmologist.
</p>
""", unsafe_allow_html=True)
