import streamlit as st
import requests
import os
from report_utils import run_pipeline

# PAGE
st.set_page_config(
    page_title="Retinal Health",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# APPLE-HEALTH CSS
st.markdown("""
<style>
.stApp { background: #f5f5f7; }
.block-container { padding-top: 2rem; padding-left: 2rem; padding-right: 2rem; }
.apple-card { background: white; border-radius: 18px; padding: 22px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
.apple-title { font-size: 28px; font-weight: 600; color: #1d1d1f; }
.apple-subtitle { font-size: 15px; color: #6e6e73; }
.metric-value { font-size: 34px; font-weight: 600; color: #1d1d1f; }
.accent { width: 6px; height: 100%; border-radius: 4px; margin-right: 14px; }
.stDownloadButton button { border-radius: 14px; height: 52px; font-size: 16px; }
hr.small { border: none; height: 1px; background: #e6e6ea; margin: 12px 0; }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown(
    '<div class="apple-card"><div class="apple-title">Retinal Health</div>'
    '<div class="apple-subtitle">AI-assisted diabetic retinopathy screening</div></div>',
    unsafe_allow_html=True
)

# SIDEBAR patient info
st.sidebar.header("Patient Information (optional)")
patient_name = st.sidebar.text_input("Patient name")
patient_age = st.sidebar.number_input("Age", min_value=0, max_value=130, step=1)
patient_id = st.sidebar.text_input("Patient ID")

# MODEL FILE ENSURE
@st.cache_resource
def ensure_model_file():
    model_path = "efficientnet_b3_state_dict.pt"
    if not os.path.exists(model_path):
        url = "https://huggingface.co/Pavansettty/DR-Pavan/resolve/main/efficientnet_b3_state_dict.pt"
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(model_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return model_path

# LAYOUT
left, right = st.columns([1.1, 1])

with left:
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    st.markdown("### Upload Fundus Image")
    uploaded = st.file_uploader("", type=["jpg","jpeg","png"], label_visibility="collapsed")
    if uploaded:
        st.image(uploaded, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    st.markdown("### Analysis")
    st.write("Upload an image to run analysis.")
    st.markdown('</div>', unsafe_allow_html=True)

# PROCESSING & RESULTS
if uploaded:
    model_path = ensure_model_file()

    # progress UI
    progress = st.progress(0)
    status_text = st.empty()

    progress.progress(10)
    status_text.info("Preparing image for analysis")

    with st.spinner("Running retinal analysis..."):
        progress.progress(30)
        status_text.info("Preprocessing and enhancement")
        cls, prob, pdf_bytes = run_pipeline(image_bytes=uploaded.read(), model_path=model_path)
        progress.progress(90)
        status_text.success("Analysis complete")
        progress.progress(100)

    # RESULT CARD (Apple style)
    STAGE_LABELS = {
        0: "No Retinopathy",
        1: "Mild",
        2: "Moderate",
        3: "Severe",
        4: "Proliferative"
    }
    COLORS = ["#34c759", "#ffd60a", "#ff9f0a", "#ff453a", "#b71c1c"]
    color = COLORS[cls]

    with right:
        st.markdown(f"""
        <div class="apple-card" style="display:flex; align-items:center;">
            <div class="accent" style="background:{color};"></div>
            <div style="flex:1;">
                <div class="apple-subtitle">Retinal Status</div>
                <div class="metric-value">{STAGE_LABELS[cls]}</div>
                <div class="apple-subtitle">Confidence · {prob*100:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Expanders for details
    from report_utils import DR_EXPLANATION, DR_ADVICE, DR_RISK_FACTORS, DR_RECOMMENDED_TESTS
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    with st.expander("About this result"):
        st.write(DR_EXPLANATION[cls])
    with st.expander("What you should do"):
        st.write(DR_ADVICE[cls])
    with st.expander("Risk factors"):
        st.write(DR_RISK_FACTORS[cls])
    with st.expander("Recommended tests"):
        st.write(DR_RECOMMENDED_TESTS[cls])
    st.markdown('</div>', unsafe_allow_html=True)

    # Patient meta shown small
    meta = f"Patient: {patient_name or '—'} • Age: {int(patient_age) if patient_age else '—'} • ID: {patient_id or '—'}"
    st.caption(meta)

    # Download button
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    st.download_button(
        "Export Health Report (PDF)",
        data=pdf_bytes,
        file_name="Retinal_Health_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
