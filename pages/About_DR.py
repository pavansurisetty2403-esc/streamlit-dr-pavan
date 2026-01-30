import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="About Diabetic Retinopathy",
    layout="wide",
)

# ================= AUTH GATE =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.switch_page("pages/Login.py")
    st.stop()


# ================= HIDE STREAMLIT DEFAULT NAV =================
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("""
    <style>
    .sidebar-container {
        display:flex;
        flex-direction:column;
        gap:18px;
        padding-top:10px;
    }

    .brand {
        font-size:28px;
        font-weight:900;
        background:linear-gradient(90deg,#5b8cff,#7cf5d3);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin-bottom:4px;
    }

    .brand-sub {
        font-size:13px;
        color:#aab2d8;
        margin-bottom:26px;
    }

    .section-title {
        font-size:26px;
        font-weight:900;
        background:linear-gradient(90deg,#6ea8ff,#7cf5d3);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin:22px 0 10px 0;
        letter-spacing:1px;
    }

    div[role="radiogroup"] label {
        font-size:18px !important;
        margin-bottom:8px;
    }

    .account-email {
        font-size:14px;
        color:#8bdcff;
        margin-bottom:12px;
    }

    .button {
        height:52px !important;
        font-size:18px !important;
        border-radius:14px !important;
        border:2px solid #5b8cff !important;
        background:transparent !important;
        color:#e6ebff !important;
    }

    .button:hover {
        background:#5b8cff !important;
        color:#0b0d12 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-container">', unsafe_allow_html=True)

    st.markdown('<div class="brand">Diabetic Retinopathy PS</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Clinical AI Screening</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "",
        ["About DR", "Reports", "History"],
        label_visibility="collapsed"
    )

    if page == "Reports":
        st.switch_page("pages/Reports.py")
    elif page == "History":
        st.switch_page("pages/History.py")

    st.markdown('<div class="section-title">Account</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="account-email">{st.session_state.get("user_email","")}</div>',
        unsafe_allow_html=True
    )

    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("pages/Login.py")


    st.markdown('</div>', unsafe_allow_html=True)

# ================= GLOBAL THEME + PULSE EFFECT =================
st.markdown("""
<style>
html, body {
    background: radial-gradient(1200px at 10% 10%, #1a1f2b, #0b0d12);
    color: #e6e9ef;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
}

/* HERO */
.hero {
    padding: 64px 56px;
    border-radius: 28px;
    background:
      linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0)),
      radial-gradient(900px at 0% 0%, rgba(90,140,255,0.25), transparent 60%);
    box-shadow: 0 40px 90px rgba(0,0,0,0.6);
    margin-bottom: 56px;
}
.hero h1 {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(90deg, #5b8cff, #7cf5d3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* SECTIONS */
.section {
    max-width: 1100px;
    margin: 0 auto 64px auto;
    padding: 56px;
    border-radius: 32px;
    background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015));
    box-shadow: 0 50px 120px rgba(0,0,0,0.6);
}

.section-title {
    font-size: 40px;
    font-weight: 700;
    margin-bottom: 18px;
    background: linear-gradient(90deg, #5b8cff, #7cf5d3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 28px;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #5b8cff, #7cf5d3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

p {
    font-size: 16px;
    line-height: 1.7;
    color: #cfd5e2;
    max-width: 900px;
}

/* INFO CARD */
.info-card {
    margin-top: 28px;
    padding: 26px 28px;
    border-radius: 22px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}

/* PULSE EFFECT */
@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 rgba(124,245,211,0.0); }
    50% { box-shadow: 0 0 28px rgba(124,245,211,0.35); }
    100% { box-shadow: 0 0 0 rgba(124,245,211,0.0); }
}
.pulse-card {
    animation: pulseGlow 3.5s ease-in-out infinite;
}

ul {
    margin-top: 10px;
    padding-left: 18px;
    color: #cfd5e2;
}
li {
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ================= HERO =================
st.markdown("""
<div class="hero">
  <h1>Diabetic Retinopathy PS</h1>
  <p style="max-width:760px; color:#aab0c0; font-size:17px">
    AI-powered clinical screening platform for early detection,
    risk assessment, and reporting of diabetic retinopathy.
  </p>
</div>
""", unsafe_allow_html=True)

# ================= CONTENT =================
st.markdown("""
<div class="section">

  <h2 class="section-title">What is Diabetic Retinopathy?</h2>
  <p>
    Diabetic Retinopathy (DR) is a progressive eye disease caused by long-term diabetes.
    High blood sugar levels damage the tiny blood vessels of the retina, the
    light-sensitive tissue at the back of the eye that enables vision.
  </p>
  <p>
    Over time, these damaged vessels may leak fluid, become blocked,
    or grow abnormally, leading to vision impairment and potentially
    permanent blindness if not detected early.
  </p>

  <h3 class="sub-title">Why it is dangerous</h3>
  <div class="info-card pulse-card">
    <p>
      Diabetic retinopathy often has no symptoms in its early stages.
      By the time visual changes appear, significant and irreversible
      retinal damage may already have occurred.
    </p>
  </div>

  <h3 class="sub-title">Who is at risk?</h3>
  <ul>
    <li>People with diabetes for more than 5–10 years</li>
    <li>Poor blood sugar control (high HbA1c)</li>
    <li>High blood pressure or high cholesterol</li>
    <li>Kidney disease or obesity</li>
    <li>Smoking or sedentary lifestyle</li>
  </ul>

  <h3 class="sub-title">Why early screening matters</h3>
  <div class="info-card pulse-card">
    <p>
      Early screening allows treatment before vision loss begins.
      With timely diagnosis and proper care, the risk of blindness
      due to diabetic retinopathy can be reduced by more than 90%.
    </p>
  </div>

  <h3 class="sub-title">Prevention & eye care</h3>
  <ul>
    <li>Maintain strict blood sugar control</li>
    <li>Monitor HbA1c levels regularly</li>
    <li>Control blood pressure and cholesterol</li>
    <li>Get a comprehensive eye exam at least once a year</li>
    <li>Seek immediate medical care for sudden vision changes</li>
  </ul>

</div>
""", unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("""
<p style="text-align:center; color:#9aa4b2; margin-bottom:40px">
Educational content only. Always consult a certified ophthalmologist.
</p>
""", unsafe_allow_html=True)
