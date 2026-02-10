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
st.caption(
    "A profection year is the life area that gets emphasized from one birthday to the next. "
    "Think of it as this year’s primary theme."
)

st.subheader("House Focus")
st.write(content["house_focus"]["label"])
st.write(content["house_focus"]["llm_text"])

if content.get("ruling_planet_section"):
    st.subheader("Ruling Planet")
    st.write(f"**{content['ruling_planet_section']['planet']}**")
    st.write(content["ruling_planet_section"]["llm_text"])
else:
    st.caption("Ruling-planet detail is limited in birth-date-only mode.")

st.subheader("How the Year Unfolds")
for item in content.get("timeline", []):
    st.write(f"**{item['segment']}**")
    st.write(item["llm_text"])

prompts = content.get("practices_and_prompts", [])
if prompts:
    st.subheader("Work With This Year")
    st.caption("Pick one prompt and write a short reflection you can revisit later.")
    for idx, prompt in enumerate(prompts, start=1):
        st.write(f"{idx}. {prompt}")
        if st.button(f"Use Prompt {idx}", key=f"year_prompt_{idx}"):
            st.session_state["yearly_reflection_text"] = f"{prompt}\n\n"

    reflection_text = st.text_area(
        "Your yearly reflection",
        key="yearly_reflection_text",
        placeholder="Write what this year is asking from you in practical terms...",
    )
    if st.button("Save Reflection", type="primary"):
        if not reflection_text.strip():
            st.warning("Add a short reflection before saving.")
        else:
            service.record_reaction(
                user_id=user.id,
                reaction="thinking",
                journal_text=reflection_text.strip(),
                reading_id=reading.id,
            )
            st.success("Reflection saved to your journal history.")

for note in content.get("disclaimers", []):
    st.warning(note)
