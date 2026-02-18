from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.constants import REACTION_CHOICES
from app.services.reading_service import ReadingService
from app.ui.components import app_header, auth_sidebar, render_unicorn_scene
from app.ui.session import init_session, require_auth

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide", initial_sidebar_state="collapsed")
init_session()
user = require_auth()
auth_sidebar(user)
service = ReadingService()

now = datetime.now()
app_header("Home", f"Good {('morning' if now.hour < 12 else 'afternoon' if now.hour < 18 else 'evening')}, {user.first_name}")
st.caption(now.strftime("%A, %B %d, %Y"))

context = service.home_context(user)
st.info(context["trust_strip"])

st.subheader("Cosmic Scene")
render_unicorn_scene()

daily = context["daily"]
moon = context["moon"]

st.subheader("Daily Horoscope")
st.markdown(f"### {daily['content']['headline']}")
st.write(daily["content"]["general"])
st.write(f"**Love:** {daily['content']['love']}")
st.write(f"**Career:** {daily['content']['career']}")
st.write(f"**Wellness:** {daily['content']['wellness']}")

with st.form("home_reaction_form"):
    reaction = st.radio(
        "How did this land?",
        options=REACTION_CHOICES,
        horizontal=True,
        format_func=lambda x: {"accurate": "🎯 accurate", "thinking": "🤔 thinking", "missed": "❌ missed"}[x],
    )
    journal = st.text_area("Optional note")
    reacted = st.form_submit_button("Save reaction")
if reacted:
    service.record_reaction(
        user_id=user.id,
        reaction=reaction,
        journal_text=journal.strip() or None,
        daily_horoscope_id=daily["id"],
    )
    st.success("Reaction saved.")

st.divider()
st.subheader("Premium Services")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### Origin Chart")
    st.write("Every answer starts here.")
    st.page_link("pages/11_Origin_Chart.py", label="Open Origin Chart")
with col2:
    st.markdown("#### Between Us")
    st.write("More than a percentage.")
    st.page_link("pages/13_Between_Us.py", label="Open Between Us")
with col3:
    st.markdown("#### Yearly Chart")
    st.write("Your year has a theme.")
    st.page_link("pages/14_Yearly_Chart.py", label="Open Yearly Chart")

st.divider()
st.subheader("Moon Phase")
st.write(f"**{moon['content']['phase'].replace('_', ' ').title()}**")
st.write(moon["content"]["insight"])
