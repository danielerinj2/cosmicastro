from __future__ import annotations

import streamlit as st

from app.services.auth_service import AuthService
from app.ui.components import app_header, auth_sidebar
from app.ui.session import get_current_user, init_session, login_user

st.set_page_config(page_title="Sign In", page_icon="🔐", layout="wide")
init_session()
current_user = get_current_user()
auth_sidebar(current_user)
auth = AuthService()

app_header("Auth - Sign In", "Access your chart and readings.")

if current_user:
    st.switch_page("pages/10_Home.py")
    st.stop()

with st.form("signin_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Sign In")

if submitted:
    result = auth.sign_in(email=email, password=password)
    if result.ok and result.user:
        login_user(result.user)
        st.success(result.message)
        st.rerun()
    else:
        st.error(result.message)

st.divider()
st.subheader("Forgot password?")
with st.form("forgot_password_form"):
    reset_email = st.text_input("Account email")
    reset_submitted = st.form_submit_button("Send reset email")

if reset_submitted:
    result = auth.request_password_reset(reset_email)
    if result.ok:
        st.success(result.message)
    else:
        st.error(result.message)
