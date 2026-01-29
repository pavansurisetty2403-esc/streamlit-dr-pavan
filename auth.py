import streamlit as st
from supabase import create_client
from supabase_auth.errors import AuthApiError

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def signup(email, password):
    try:
        return supabase.auth.sign_up({
            "email": email,
            "password": password
        })
    except AuthApiError as e:
        return e

def login(email, password):
    try:
        return supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except AuthApiError as e:
        return e

def logout():
    supabase.auth.sign_out()
