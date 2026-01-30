import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Upload History | Diabetic Retinopathy PS",
    layout="wide",
)

# ================= AUTH GATE =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.switch_page("Login.py")
    st.stop()

# ================= HIDE STREAMLIT DEFAULT NAV =================
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR (MATCH ABOUT_DR EXACTLY) =================
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
        index=2,
        label_visibility="collapsed"
    )

    if page == "About DR":
        st.switch_page("pages/About_DR.py")
    elif page == "Reports":
        st.switch_page("pages/Reports.py")

    st.markdown('<div class="section-title">Account</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="account-email">{st.session_state.get("user_email","")}</div>',
        unsafe_allow_html=True
    )

    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.switch_page("pages/Login.py")


    st.markdown('</div>', unsafe_allow_html=True)

# ================= GLOBAL THEME =================
st.markdown("""
<style>
html, body {
    background: radial-gradient(1200px at 10% 10%, #1a1f2b, #0b0d12);
    color:#e6e9ef;
    font-family:-apple-system,BlinkMacSystemFont,"Inter",sans-serif;
}

.page-title {
    font-size:44px;
    font-weight:800;
    text-align:center;
    background:linear-gradient(90deg,#5b8cff,#7cf5d3);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.user-pill {
    display:inline-block;
    margin-top:8px;
    padding:6px 14px;
    border-radius:999px;
    background:rgba(124,245,211,.18);
    color:#7cf5d3;
    font-size:13px;
}

/* ===== HISTORY LIST ===== */
.item {
    max-width:900px;
    margin:18px auto;
    padding-bottom:14px;
    border-bottom:1px solid rgba(255,255,255,.08);
}
.item:last-child {
    border-bottom:none;
}

.filename {
    font-weight:600;
    font-size:16px;
}
.timestamp {
    font-size:13px;
    color:#9aa6c7;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown(f"""
<h1 class="page-title">Upload History</h1>
<p style="text-align:center;">
<span class="user-pill">{st.session_state.get("user_email","")}</span>
</p>
""", unsafe_allow_html=True)

# ================= HISTORY (NO CARD) =================
uploads = st.session_state.get("upload_history", [])

if not uploads:
    st.markdown(
        '<p style="text-align:center;color:#9aa6c7;margin-top:40px;">No uploads yet.</p>',
        unsafe_allow_html=True
    )
else:
    for item in uploads:
        st.markdown(f"""
        <div class="item">
            <div class="filename">{item["filename"]}</div>
            <div class="timestamp">{item["timestamp"]}</div>
        </div>
        """, unsafe_allow_html=True)
