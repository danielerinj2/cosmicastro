from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.services.reading_service import ReadingService
from app.ui.components import app_header, auth_sidebar, confidence_banner, premium_upgrade_block
from app.ui.session import init_session, require_auth

st.set_page_config(page_title="Yearly Chart", page_icon="🗓️", layout="wide")
init_session()
user = require_auth()
auth_sidebar(user)
service = ReadingService()

today = datetime.now().date()
app_header("Your Yearly Chart", "Know what this year is asking of you.")

if not premium_upgrade_block(user, "Yearly Chart"):
    st.stop()

reading = service.get_or_create_yearly_chart(user, today)
content = reading.content
meta = content["meta"]

confidence_banner(
    reading.mode,
    full_text="Full profection mode: birth date, time, and place are all present.",
    light_text="Birth-date-only mode: house focus is available, ruling planet detail is intentionally limited.",
)

st.markdown(f"### {content['summary']['headline']}")
for paragraph in content["summary"]["paragraphs"]:
    st.write(paragraph)
if content["summary"].get("llm_voice"):
    st.write(content["summary"]["llm_voice"])

st.subheader("Year Meta")
st.write(f"- Age: {meta['age']}")
st.write(f"- Profection year: {meta['year_label']}")
st.write(f"- Window: {meta['window']}")
st.write(f"- Mode: {meta['mode_label']}")

st.subheader("House Focus")
st.write(content["house_focus"]["label"])
st.write(content["house_focus"]["llm_text"])

if content.get("ruling_planet_section"):
    st.subheader("Ruling Planet")
    st.write(f"**{content['ruling_planet_section']['planet']}**")
    st.write(content["ruling_planet_section"]["llm_text"])
else:
    st.info("Add birth time and place in Settings to unlock full ruling-planet details.")

st.subheader("How the Year Unfolds")
for item in content.get("timeline", []):
    st.write(f"**{item['segment']}**")
    st.write(item["llm_text"])

st.subheader("Practices and Prompts")
for prompt in content.get("practices_and_prompts", []):
    st.write(f"- {prompt}")

for note in content.get("disclaimers", []):
    st.warning(note)
