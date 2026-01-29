import streamlit as st
from auth import signup, login
from supabase_auth.errors import AuthApiError

st.set_page_config(page_title="Login", layout="centered")

# ---------- SESSION INIT ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.title("User Login")

tab_login, tab_signup = st.tabs(["Login", "Create Account"])

# ===================== LOGIN =====================
with tab_login:
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        if not email or not password:
            st.warning("Email and password are required.")
        else:
            res = login(email, password)

            if hasattr(res, "user") and res.user:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.switch_page("app.py")


            elif isinstance(res, AuthApiError):
                msg = str(res)
                if "Email not confirmed" in msg:
                    st.warning("Email not verified. Please check your inbox and confirm your email.")
                elif "Invalid login credentials" in msg:
                    st.error("Incorrect email or password.")
                else:
                    st.error(msg)
            else:
                st.error(str(res))

# ===================== SIGNUP =====================
with tab_signup:
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password (min 6 chars)", type="password", key="signup_password")

    if st.button("Create Account", key="signup_btn"):
        if not new_email or not new_password:
            st.warning("Email and password are required.")
        else:
            res = signup(new_email, new_password)

            if hasattr(res, "user") and res.user:
                st.success("Account created successfully.")
                st.info("Please check your email and confirm your account before logging in.")

            elif isinstance(res, AuthApiError):
                msg = str(res)
                if "User already registered" in msg:
                    st.error("Account already exists. Please login.")
                else:
                    st.error(msg)
            else:
                st.error(str(res))
