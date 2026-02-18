from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.constants import REACTION_CHOICES
from app.services.reading_service import ReadingService
from app.ui.components import app_header, auth_sidebar
from app.ui.session import init_session, require_auth

st.set_page_config(page_title="Daily Horoscope", page_icon="📅", layout="wide", initial_sidebar_state="collapsed")
init_session()
user = require_auth()
auth_sidebar(user)
service = ReadingService()

today = datetime.now().date()
daily = service.get_or_create_daily_horoscope(user, today)

app_header("Daily Horoscope", f"{today.isoformat()} · {user.sun_sign or 'Your sign'}")

content = daily["content"]
st.markdown(f"### {content['headline']}")
st.write(content["general"])

st.subheader("Love and Relationships")
st.write(content["love"])
st.subheader("Career and Purpose")
st.write(content["career"])
st.subheader("Wellness")
st.write(content["wellness"])

with st.form("daily_reaction_form"):
    reaction = st.radio(
        "How did this land today?",
        options=REACTION_CHOICES,
        horizontal=True,
        format_func=lambda x: {"accurate": "🎯 accurate", "thinking": "🤔 thinking", "missed": "❌ missed"}[x],
    )
    journal = st.text_area("Optional journal note")
    submitted = st.form_submit_button("Save")

if submitted:
    service.record_reaction(
        user_id=user.id,
        reaction=reaction,
        journal_text=journal.strip() or None,
        daily_horoscope_id=daily["id"],
    )
    st.success("Saved.")
