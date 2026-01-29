import streamlit as st
from auth import login, signup
from supabase_auth.errors import AuthApiError

st.set_page_config(
    page_title="Diabetic Retinopathy PS | Login",
    layout="centered"
)

# ---------------- SESSION INIT ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ---------------- CSS ----------------
st.markdown("""
<style>
html, body {
    background: radial-gradient(1200px at 10% 10%, #1a2235, #0b0f1a);
}

/* Kill Streamlit default container */
section.main > div:first-child {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
}

/* Login card */
.login-wrapper {
    max-width: 720px;
    margin: 10vh auto;
    padding: 60px 56px 48px 56px; /* Increased top padding to 60px for better centering */
    border-radius: 28px;
    background: linear-gradient(
        145deg,
        rgba(40,60,110,0.35),
        rgba(10,15,25,0.55)
    );
    backdrop-filter: blur(18px);
    box-shadow:
        inset 0 0 0 1px rgba(120,160,255,0.12),
        0 30px 80px rgba(0,0,0,0.6);
}

/* Title */
.login-title {
    text-align: center;
    font-size: 38px;
    font-weight: 700;
    background: linear-gradient(90deg,#6ea8ff,#8bdcff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
}

/* Subtitle */
.login-subtitle {
    text-align: center;
    color: #a8b3cf;
    font-size: 14px;
    margin-bottom: 32px; /* Increased margin to separate from tabs */
}

/* Tabs */
div[data-baseweb="tab-list"] {
    justify-content: center;
    gap: 12px;
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 6px;
    margin-bottom: 24px;
    max-width: 360px;
    margin-left: auto;
    margin-right: auto;
}

button[data-baseweb="tab"] {
    min-width: 160px;
    font-size: 15px;
    font-weight: 600;
    color: #cfd6ee;
}

button[aria-selected="true"] {
    background: linear-gradient(90deg,#3b82f6,#60a5fa);
    color: white !important;
    border-radius: 10px;
}

/* Inputs */
input {
    background: rgba(15,25,45,0.75) !important;
    border: 1px solid rgba(120,160,255,0.18) !important;
    border-radius: 14px !important;
    padding: 14px !important;
    color: #e6ebff !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg,#3b82f6,#60a5fa);
    color: white;
    font-weight: 600;
    border-radius: 14px;
    height: 52px;
    border: none;
    margin-top: 18px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------

# Opening the wrapper div
st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

# Title and Subtitle are now explicitly placed inside the wrapper
st.markdown('<div class="login-title">Diabetic Retinopathy PS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="login-subtitle">AI-powered retinal screening for early diabetic eye disease detection</div>',
    unsafe_allow_html=True
)

tab_login, tab_signup = st.tabs(["Login", "Create Account"])

# ---------------- LOGIN ----------------
with tab_login:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        with st.spinner("Authenticating"):
            res = login(email, password)

        if hasattr(res, "user") and res.user:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.rerun()
        elif isinstance(res, AuthApiError):
            st.error("Invalid login credentials")

# ---------------- SIGNUP ----------------
with tab_signup:
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password (min 6 chars)", type="password")

    if st.button("Create Account", use_container_width=True):
        with st.spinner("Creating account"):
            res = signup(new_email, new_password)

        if hasattr(res, "user") and res.user:
            st.success("Account created. Verify email before login.")
        elif isinstance(res, AuthApiError):
            st.error("Signup failed")

# Closing the wrapper div
st.markdown('</div>', unsafe_allow_html=True)