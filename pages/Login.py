import streamlit as st
from auth import signup, login
from supabase_auth.errors import AuthApiError

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Diabetic Retinopathy PS | Login",
    layout="centered",
)

# ================= SESSION =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# ================= STYLES =================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(1200px at 10% 10%, #1a1f2b, #0b0d12);
    color: #e6e9ef;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
}
[data-testid="stSidebar"] { display: none; }

/* ---------- Card ---------- */
.auth-card {
    max-width: 560px;
    margin: 80px auto;
    padding: 56px 52px;
    border-radius: 28px;
    background:
      linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0)),
      radial-gradient(900px at 0% 0%, rgba(90,140,255,0.22), transparent 60%);
    box-shadow: 0 40px 80px rgba(0,0,0,0.65);
}

/* ---------- Header ---------- */
.auth-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #5b8cff, #7cf5d3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.auth-sub {
    font-size: 15px;
    color: #aab0c0;
    margin-bottom: 34px;
}

/* ---------- Segmented control ---------- */
.segment {
    display: flex;
    gap: 10px;
    margin-bottom: 32px;
}
.segment button {
    flex: 1;
    background: rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    padding: 12px !important;
    font-weight: 600 !important;
    color: #c3c8d4 !important;
}
.segment button.active {
    background: linear-gradient(90deg, #5b8cff, #7cf5d3) !important;
    color: #0b0d12 !important;
    border: none !important;
}

/* ---------- Inputs ---------- */
input {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    padding: 14px !important;
    color: #e6e9ef !important;
}
input:focus {
    border-color: rgba(124,245,211,0.6) !important;
    box-shadow: 0 0 0 1px rgba(124,245,211,0.25) !important;
}

/* ---------- Main button ---------- */
.main-btn {
    background: linear-gradient(90deg, #5b8cff, #7cf5d3) !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 10px 30px rgba(91,140,255,0.35);
}

/* ---------- Footer ---------- */
.auth-foot {
    margin-top: 26px;
    font-size: 13px;
    color: #9aa4b2;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ================= CARD START =================
st.markdown('<div class="auth-card">', unsafe_allow_html=True)

# ---------- HEADER INSIDE CARD ----------
st.markdown('<div class="auth-title">Diabetic Retinopathy PS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="auth-sub">'
    'AI-powered retinal screening for early diabetic eye disease detection'
    '</div>',
    unsafe_allow_html=True
)

# ---------- Segmented buttons ----------
c1, c2 = st.columns(2)

with c1:
    if st.button("Login", use_container_width=True):
        st.session_state.auth_mode = "login"

with c2:
    if st.button("Create Account", use_container_width=True):
        st.session_state.auth_mode = "signup"

# ================= FORMS =================
if st.session_state.auth_mode == "login":
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
            st.error(str(e))

else:
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password (min 6 characters)", type="password")

    if st.button("Create Account", use_container_width=True):
        try:
            res = signup(new_email, new_password)
            if res.user:
                st.success("Account created. Please check your email to verify.")
        except AuthApiError as e:
            st.error(str(e))

st.markdown(
    '<div class="auth-foot">🔒 Secure • 🩺 Medical-grade • 🤖 AI-assisted</div>',
    unsafe_allow_html=True
)

# ================= CARD END =================
st.markdown('</div>', unsafe_allow_html=True)
