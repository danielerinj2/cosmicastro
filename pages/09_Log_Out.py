from __future__ import annotations

import streamlit as st

from app.ui.session import init_session, logout_user

st.set_page_config(page_title="Log Out", page_icon="🚪", layout="wide", initial_sidebar_state="collapsed")

init_session()
logout_user()
st.switch_page("streamlit_app.py")
