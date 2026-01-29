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

footer {visibility: hidden;}
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
<b>Diabetic Retinopathy (DR)</b> is a diabetes-related eye disease caused by damage
to the small blood vessels of the retina. It often develops silently in early
stages and may progress to <b>irreversible vision loss</b> if not detected early.
</p>

<h3>Stages of Diabetic Retinopathy</h3>
<ul>
<li><b>No DR</b> – Healthy retina with no visible abnormalities</li>
<li><b>Mild</b> – Microaneurysms begin to appear</li>
<li><b>Moderate</b> – Increased leakage and vessel blockage</li>
<li><b>Severe</b> – Large areas of retinal ischemia</li>
<li><b>Proliferative</b> – Abnormal vessel growth (high risk stage)</li>
</ul>

<h3>What This Website Does</h3>
<p>
This platform uses a <b>deep learning model trained on retinal fundus images</b>
to assist in early screening of diabetic retinopathy.
</p>

<ul>
<li>Enhances and preprocesses retinal images</li>
<li>Analyzes retinal vascular patterns</li>
<li>Predicts DR stage with confidence score</li>
<li>Generates a detailed, patient-friendly PDF report</li>
</ul>

<p style="color:#9aa4b2">
For screening and educational use only. This tool does not replace professional
ophthalmic diagnosis.
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

# ================== ANALYSIS FLOW ==================
if uploaded:
    # show minimal UI feedback while processing
    with st.spinner("Analyzing retinal image…"):
        progress = st.progress(0)
        for i in range(0, 80, 8):
            time.sleep(0.03)
            progress.progress(i + 1)

        # save uploaded image to temp file for run_pipeline
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            Image.open(uploaded).convert("RGB").save(tmp.name)
            tmp_path = tmp.name

        # call run_pipeline robustly and handle different return types
        cls = None
        prob = None
        pdf_bytes = None
        error_msg = None

        try:
            result = run_pipeline(tmp_path)  # call as before

            # normalize result into (cls, prob, pdf_bytes)
            if result is None:
                error_msg = "run_pipeline returned None."
            elif isinstance(result, bytes):
                # only PDF bytes returned
                pdf_bytes = result
            elif isinstance(result, dict):
                cls = result.get("cls") or result.get("stage") or result.get("label")
                prob = result.get("prob") or result.get("confidence")
                pdf_bytes = result.get("pdf_bytes") or result.get("pdf")
            elif isinstance(result, (list, tuple)):
                if len(result) == 3:
                    cls, prob, pdf_bytes = result
                elif len(result) == 2:
                    cls, prob = result
                elif len(result) == 1:
                    # single element - could be bytes
                    first = result[0]
                    if isinstance(first, bytes):
                        pdf_bytes = first
                    elif isinstance(first, dict):
                        pdf_bytes = first.get("pdf_bytes") or first.get("pdf")
                else:
                    # unexpected tuple size
                    error_msg = f"run_pipeline returned tuple of length {len(result)}"
            else:
                # unexpected type
                error_msg = f"run_pipeline returned unsupported type: {type(result)}"

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            # show short friendly message and print full trace to app logs
            st.error("Analysis failed. See logs for details.")
            st.text_area("Error trace (for debugging)", tb, height=250)
            # stop further UI for this run
            raise

        finally:
            progress.progress(100)
            time.sleep(0.12)

    # show result (best-effort)
    if cls is not None or prob is not None:
        cls_display = cls if cls is not None else "Unknown"
        prob_display = f"{prob*100:.1f}%" if (prob is not None and isinstance(prob, (float,int))) else "Unknown"
        st.markdown(f"""
        <div class="card fade">
            <h2>Retinal Status</h2>
            <div class="status">{cls_display}</div>
            <div class="conf">Confidence: {prob_display}</div>
        </div>
        """, unsafe_allow_html=True)
    elif pdf_bytes and not (cls or prob):
        # only pdf returned
        st.markdown("""
        <div class="card fade">
            <h2>Analysis Complete</h2>
            <div class="conf">Report generated (no label returned by run_pipeline).</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if error_msg:
            st.warning(f"Analysis completed but result parsing failed: {error_msg}")
        else:
            st.warning("Analysis completed but no usable output returned by run_pipeline.")

    # export PDF (if available)
    if pdf_bytes:
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
    else:
        st.info("No PDF available to download from the analysis.")


# ================== FOOTER ==================
st.markdown("""
<p style="text-align:center; color:#9aa4b2; margin-top:40px">
Always consult a certified ophthalmologist for medical decisions.
</p>
""", unsafe_allow_html=True)
