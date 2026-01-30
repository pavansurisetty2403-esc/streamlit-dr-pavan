import streamlit as st
from auth import login, signup
from supabase_auth.errors import AuthApiError

st.set_page_config(
    page_title="Diabetic Retinopathy PS | Login",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- SESSION ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ---------------- REDIRECT AFTER LOGIN ----------------
# IMPORTANT: redirect DIRECTLY to About_DR page
if st.session_state.authenticated:
    st.switch_page("pages/About_DR.py")
    st.stop()

# ---------------- FORCE HIDE SIDEBAR ----------------
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- THEME ----------------
st.markdown("""
<style>
html, body {
    background: radial-gradient(1200px at 10% 10%, #1a1f2b, #0b0d12);
    color: #e6e9ef;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
}

section.main > div:first-child {
    background: none !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
}

.app-title {
    text-align: center;
    font-size: 40px;
    font-weight: 700;
    background: linear-gradient(90deg,#5b8cff,#7cf5d3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 12vh;
    margin-bottom: 6px;
}

.app-subtitle {
    text-align: center;
    color: #aab0c0;
    font-size: 15px;
    margin-bottom: 28px;
}

div[data-baseweb="tab-list"] {
    justify-content: center;
    gap: 12px;
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 6px;
    max-width: 360px;
    margin: 0 auto 28px auto;
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

input {
    background: rgba(15,25,45,0.75) !important;
    border: 1px solid rgba(120,160,255,0.18) !important;
    border-radius: 14px !important;
    padding: 14px !important;
    color: #e6ebff !important;
}

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
st.markdown('<div class="app-title">Diabetic Retinopathy PS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">AI-powered retinal screening for early diabetic eye disease detection</div>',
    unsafe_allow_html=True
)

tab_login, tab_signup = st.tabs(["Login", "Create Account"])

# ---------------- LOGIN ----------------
with tab_login:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
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
        res = signup(new_email, new_password)

        if hasattr(res, "user") and res.user:
            st.success("Account created. Verify your email before login.")
        elif isinstance(res, AuthApiError):
            st.error("Signup failed")
