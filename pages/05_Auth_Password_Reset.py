from __future__ import annotations

import streamlit as st

from app.services.auth_service import AuthService
from app.ui.components import app_header, auth_sidebar
from app.ui.session import get_current_user, init_session

st.set_page_config(page_title="Password Reset", page_icon="♻️", layout="wide")
init_session()
auth_sidebar(get_current_user())
auth = AuthService()

app_header("Auth - Password Reset", "Use token from email to reset password manually.")

params = st.query_params
prefill_token = params.get("rt") or params.get("reset_token") or params.get("token")
if isinstance(prefill_token, list):
    prefill_token = prefill_token[0] if prefill_token else ""

with st.form("manual_password_reset_form"):
    token = st.text_input("Reset token", value=prefill_token or "")
    new_password = st.text_input("New password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")
    submitted = st.form_submit_button("Reset Password")

if submitted:
    if not token.strip() or not new_password:
        st.error("Token and new password are required.")
    elif new_password != confirm_password:
        st.error("Passwords do not match.")
    else:
        result = auth.reset_password(token_value=token.strip(), new_password=new_password)
        if result.ok:
            st.success(result.message)
        else:
            st.error(result.message)
