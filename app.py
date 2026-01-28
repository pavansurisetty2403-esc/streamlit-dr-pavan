import streamlit as st
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import requests
import os

@st.cache_resource
def load_model():
    model_path = "efficientnet_b3_best.pt"

    if not os.path.exists(model_path):
        url = "https://huggingface.co/pavansurisetty/aptos-dr-model/resolve/main/efficientnet_b3_best.pt"
        r = requests.get(url)
        with open(model_path, "wb") as f:
            f.write(r.content)

    model = models.efficientnet_b3(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 5)

    state_dict = torch.load(
    model_path,
    map_location="cpu",
    weights_only=True
)

    model.load_state_dict(state_dict)
    model.eval()
    return model

model = load_model()

tfms = transforms.Compose([
    transforms.Resize((380, 380)),
    transforms.ToTensor()
])

st.title("Diabetic Retinopathy Detection")

uploaded = st.file_uploader("Upload fundus image", type=["jpg", "png", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, use_column_width=True)

    x = tfms(img).unsqueeze(0)

    with torch.no_grad():
        out = model(x)
        pred = out.argmax(dim=1).item()

    st.write("Predicted Class:", pred)
