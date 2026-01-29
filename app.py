import streamlit as st
import torch
import torch.nn as nn
from torchvision import models
import requests
import os
from report_utils import run_pipeline

st.set_page_config(page_title="Diabetic Retinopathy Detection", layout="centered")

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


st.title("🩺 Diabetic Retinopathy Detection & Report")

uploaded = st.file_uploader(
    "Upload Fundus Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded:
    st.image(uploaded, caption="Uploaded Fundus Image", use_column_width=True)

    model_path = ensure_model_file()

    with st.spinner("Analyzing image and generating detailed medical report..."):
        cls, prob, pdf_bytes = run_pipeline(
            image_bytes=uploaded.read(),
            model_path=model_path
        )

    st.success(f"Predicted DR Stage: {cls}")
    st.write(f"Confidence: {prob * 100:.2f}%")

    st.download_button(
        label="⬇️ Download Detailed PDF Medical Report",
        data=pdf_bytes,
        file_name="Diabetic_Retinopathy_Report.pdf",
        mime="application/pdf"
    )
