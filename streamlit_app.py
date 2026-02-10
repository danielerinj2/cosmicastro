from __future__ import annotations

import streamlit as st

from app.services.auth_service import AuthService
from app.ui.components import app_header, auth_sidebar
from app.ui.session import get_current_user, init_session

st.set_page_config(
    page_title="Discover Your Cosmic Self",
    page_icon="✨",
    layout="wide",
)

init_session()
try:
    auth = AuthService()
    user = get_current_user()
except Exception as exc:
    auth = None
    user = None
    st.error("App configuration is incomplete. Please check Streamlit Cloud Secrets.")
    st.code(str(exc))
    st.stop()

auth_sidebar(user)

params = st.query_params
verify_token = params.get("verify_token")
reset_token = params.get("reset_token")

app_header(
    "Discover Your Cosmic Self",
    "MVP workspace with Supabase, Groq, and SendGrid wired.",
)

if verify_token:
    result = auth.verify_email(verify_token)
    if result.ok:
        st.success(result.message)
    else:
        st.error(result.message)
    st.query_params.clear()

if reset_token:
    st.subheader("Reset Password")
    with st.form("reset_via_link_form"):
        new_password = st.text_input("New password", type="password")
        new_password_confirm = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Reset Password")

    if submitted:
        if not new_password or new_password != new_password_confirm:
            st.error("Passwords must match.")
        else:
            result = auth.reset_password(token_value=reset_token, new_password=new_password)
            if result.ok:
                st.success(result.message)
                st.query_params.clear()
            else:
                st.error(result.message)

st.markdown("### Start Here")
st.write("Use the sidebar to open:")
st.write("- `Auth - Sign Up`")
st.write("- `Auth - Sign In`")
st.write("- `Home` once signed in")
st.write("- `Supabase Connection Check` and `SendGrid Connection Check` for infrastructure validation")
