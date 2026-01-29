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

/* ---------- Global ---------- */
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(1200px at 10% 10%, #1a1f2b, #0b0d12);
    color: #e6e9ef;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
}
[data-testid="stSidebar"] { display: none; }

/* ---------- Card ---------- */
.auth-card {
    max-width: 520px;
    margin: 90px auto 0 auto;
    padding: 56px 48px;
    border-radius: 28px;
    background:
      linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0)),
      radial-gradient(800px at 0% 0%, rgba(90,140,255,0.22), transparent 60%);
    box-shadow: 0 40px 80px rgba(0,0,0,0.6);
}

/* ---------- Title ---------- */
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
    margin-bottom: 36px;
}

/* ---------- Segmented control ---------- */
.segment {
    display: flex;
    background: rgba(255,255,255,0.05);
    border-radius: 999px;
    padding: 6px;
    margin-bottom: 32px;
}
.segment button {
    flex: 1;
    background: transparent !important;
    border-radius: 999px !important;
    border: none !important;
    padding: 12px !important;
    font-weight: 600 !important;
    color: #9aa4b2 !important;
    box-shadow: none !important;
}
.segment button.active {
    background: linear-gradient(90deg, #5b8cff, #7cf5d3) !important;
    color: #0b0d12 !important;
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
    border-radius: 999px !important;
    padding: 14px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 10px 30px rgba(91,140,255,0.35);
}

/* ---------- Footer ---------- */
.auth-foot {
    margin-top: 22px;
    font-size: 13px;
    color: #9aa4b2;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ================= UI =================
st.markdown('<div class="auth-card">', unsafe_allow_html=True)

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

# Inject active state
st.markdown(f"""
<script>
const buttons = window.parent.document.querySelectorAll("button");
buttons.forEach(btn => {{
  if (btn.innerText === "{'Login' if st.session_state.auth_mode=='login' else 'Create Account'}") {{
    btn.classList.add("active");
  }}
}});
</script>
""", unsafe_allow_html=True)

# ================= FORMS =================
if st.session_state.auth_mode == "login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True, key="login_btn"):
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

else:
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password (min 6 characters)", type="password")

    if st.button("Create Account", use_container_width=True, key="signup_btn"):
        try:
            res = signup(new_email, new_password)
            if res.user:
                st.success("Account created.")
                st.info("Check your email to confirm before logging in.")
        except AuthApiError as e:
            st.error(str(e))

st.markdown(
    '<div class="auth-foot">🔒 Secure • 🩺 Medical-grade • 🤖 AI-assisted</div>',
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
