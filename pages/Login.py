import streamlit as st
from auth import signup, login
from supabase_auth.errors import AuthApiError

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Diabetic Retinopathy PS | Login",
    layout="centered"
)

# ================= SESSION INIT =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ================= STYLES =================
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #121826, #0b0f14);
    color: #e6edf3;
}

/* Card */
.login-card {
    background: #121826;
    border-radius: 14px;
    padding: 2.5rem;
    border: 1px solid rgba(47,129,247,0.25);
    box-shadow: 0 0 30px rgba(47,129,247,0.15);
}

/* Titles */
.app-title {
    font-size: 2.1rem;
    font-weight: 700;
    text-align: center;
    color: #e6edf3;
}
.app-subtitle {
    text-align: center;
    font-size: 0.95rem;
    color: #9aa4b2;
    margin-bottom: 1.8rem;
}

/* Tabs */
[data-baseweb="tab"] {
    font-weight: 600;
    color: #9aa4b2;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #2f81f7;
    border-bottom: 2px solid #2f81f7;
}

/* Inputs */
input {
    background-color: #0b0f14 !important;
    color: #e6edf3 !important;
    border: 1px solid rgba(47,129,247,0.25) !important;
}

/* Buttons */
button {
    background: linear-gradient(135deg, #2f81f7, #1f6feb) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Footer text */
.trust {
    text-align: center;
    font-size: 0.85rem;
    color: #9aa4b2;
    margin-top: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ================= UI =================
st.markdown('<div class="login-card">', unsafe_allow_html=True)

st.markdown('<div class="app-title">Diabetic Retinopathy PS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">'
    'AI-powered retinal screening system for early diabetic eye disease detection'
    '</div>',
    unsafe_allow_html=True
)

tab_login, tab_signup = st.tabs(["Login", "Create Account"])

# ================= LOGIN =================
with tab_login:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        try:
            res = login(email, password)
            if res.user:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.switch_page("app.py")
        except AuthApiError as e:
            msg = str(e)
            if "Email not confirmed" in msg:
                st.warning("Please verify your email before logging in.")
            elif "Invalid login credentials" in msg:
                st.error("Incorrect email or password.")
            else:
                st.error("Login failed.")

# ================= SIGNUP =================
with tab_signup:
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password (min 6 characters)", type="password")

    if st.button("Create Account", use_container_width=True):
        try:
            res = signup(new_email, new_password)
            if res.user:
                st.success("Account created successfully.")
                st.info("Please check your email to confirm your account before logging in.")
        except AuthApiError as e:
            st.error(str(e))

st.markdown(
    '<div class="trust">🔒 Secure • 🩺 Medical-grade • 🤖 AI-assisted</div>',
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
