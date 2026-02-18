from __future__ import annotations

from datetime import date

import streamlit as st

from app.services.auth_service import AuthService
from app.ui.components import app_header, auth_sidebar, parse_time_ampm
from app.ui.session import get_current_user, init_session, login_user

st.set_page_config(page_title="Sign Up", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")
init_session()
current_user = get_current_user()
auth_sidebar(current_user)
auth = AuthService()

app_header("Auth - Sign Up", "Create your account and save your birth data.")

if current_user:
    st.switch_page("pages/10_Home.py")
    st.stop()

first_name = st.text_input("First name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
dob = st.date_input("Date of birth", value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
knows_birth_time = st.checkbox("I know my birth time", value=False)
birth_time = None
if knows_birth_time:
    birth_time_raw = st.text_input(
        "Birth time (AM/PM)",
        placeholder="e.g. 09:30 AM",
        key="signup_birth_time_ampm",
    )
    st.caption("Use format `HH:MM AM/PM`.")
    birth_time = parse_time_ampm(birth_time_raw)
else:
    st.session_state["signup_birth_time_ampm"] = ""
birth_location = st.text_input("Birth location (city, country)", placeholder="e.g. Mumbai, India")
submitted = st.button("Create Account", type="primary")

if submitted:
    if not first_name.strip() or not email.strip() or not password:
        st.error("First name, email, and password are required.")
    elif knows_birth_time and birth_time is None:
        st.error("Please enter birth time in `HH:MM AM/PM` format.")
    else:
        result = auth.sign_up(
            first_name=first_name.strip(),
            email=email.strip(),
            password=password,
            dob=dob,
            birth_time=birth_time.isoformat() if birth_time else None,
            birth_location=birth_location.strip() or None,
        )
        if result.ok and result.user:
            login_user(result.user)
            st.success(result.message)
            st.info("Verification email sent. You can use the app now; verification is enforced before premium purchases.")
            st.rerun()
        else:
            st.error(result.message)
