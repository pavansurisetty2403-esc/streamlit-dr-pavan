import streamlit as st
from auth import login, signup
from supabase_auth.errors import AuthApiError
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Diabetic Retinopathy PS | Login",
    layout="wide",
)

# ---------------- SESSION INIT ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background: radial-gradient(1200px at 10% 10%, #1a2233, #0b0f16);
    color: #e6e9ef;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
}

/* Center wrapper */
.auth-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 90vh;
}

/* Glass card */
.auth-card {
    width: 460px;
    padding: 36px 36px 42px 36px;
    border-radius: 22px;
    background: linear-gradient(
        180deg,
        rgba(40, 56, 88, 0.55),
        rgba(20, 28, 44, 0.55)
    );
    backdrop-filter: blur(18px);
    border: 1px solid rgba(120, 160, 255, 0.12);
    box-shadow: 0 30px 80px rgba(0,0,0,0.55);
}

/* Title */
.auth-title {
    text-align: center;
    font-size: 34px;
    font-weight: 700;
    background: linear-gradient(90deg, #6ea8ff, #7dd3fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
}

/* Subtitle */
.auth-sub {
    text-align: center;
    font-size: 14px;
    color: #9aa4b2;
    margin-bottom: 26px;
}

/* Segment control */
.segment {
    display: flex;
    gap: 8px;
    background: rgba(10,15,25,0.6);
    padding: 6px;
    border-radius: 14px;
    margin-bottom: 22px;
}

.segment button {
    flex: 1;
    padding: 10px 0;
    border-radius: 10px;
    border: none;
    background: transparent;
    color: #c7d2fe;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
}

.segment button.active {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    box-shadow: 0 6px 20px rgba(59,130,246,0.45);
}

/* Inputs */
.stTextInput input {
    background: rgba(15, 22, 36, 0.85);
    border: 1px solid rgba(120,160,255,0.15);
    border-radius: 12px;
    color: #e6e9ef;
    padding: 12px;
}

/* Primary button */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    border: none;
    border-radius: 14px;
    padding: 12px;
    font-size: 15px;
    font-weight: 600;
    color: white;
    box-shadow: 0 10px 30px rgba(59,130,246,0.45);
}

.stButton > button:hover {
    transform: translateY(-1px);
}

/* Footer */
.auth-footer {
    text-align: center;
    font-size: 12px;
    color: #8b95a5;
    margin-top: 18px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI LAYOUT ----------------
st.markdown('<div class="auth-wrapper"><div class="auth-card">', unsafe_allow_html=True)

st.markdown('<div class="auth-title">Diabetic Retinopathy PS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="auth-sub">AI-powered retinal screening for early diabetic eye disease detection</div>',
    unsafe_allow_html=True
)

# ---------------- SEGMENT SWITCH ----------------
c1, c2 = st.columns(2)

with c1:
    if st.button(
        "Login",
        key="seg_login",
        use_container_width=True
    ):
        st.session_state.auth_mode = "login"

with c2:
    if st.button(
        "Create Account",
        key="seg_signup",
        use_container_width=True
    ):
        st.session_state.auth_mode = "signup"

# Apply active styling (CSS hook)
st.markdown("""
<script>
const buttons = window.parent.document.querySelectorAll('button');
buttons.forEach(b => {
    if (b.innerText === "Login" && "%s" === "login") b.classList.add("active");
    if (b.innerText === "Create Account" && "%s" === "signup") b.classList.add("active");
});
</script>
""" % (st.session_state.auth_mode, st.session_state.auth_mode), unsafe_allow_html=True)

# ---------------- FORM ----------------
email = st.text_input("Email")
password = st.text_input("Password", type="password")

# ---------------- ACTION ----------------
if st.session_state.auth_mode == "login":
    if st.button("Login", key="login_submit", use_container_width=True):
        with st.spinner("Signing you in..."):
            time.sleep(0.6)
            try:
                res = login(email, password)
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.switch_page("app.py")
            except AuthApiError as e:
                msg = str(e)
                if "Email not confirmed" in msg:
                    st.warning("Please verify your email before logging in.")
                else:
                    st.error("Invalid email or password.")

else:
    if st.button("Create Account", key="signup_submit", use_container_width=True):
        with st.spinner("Creating account..."):
            time.sleep(0.6)
            try:
                signup(email, password)
                st.success("Account created. Check your email to verify.")
            except AuthApiError as e:
                st.error(str(e))

st.markdown(
    '<div class="auth-footer">🔒 Secure • Medical-grade • AI-assisted</div>',
    unsafe_allow_html=True
)

st.markdown('</div></div>', unsafe_allow_html=True)
