from __future__ import annotations

from typing import Any

import streamlit as st

from app.services.llm_service import LLMService
from app.services.reading_service import ReadingService
from app.ui.components import app_header, auth_sidebar
from app.ui.session import init_session, require_auth

st.set_page_config(page_title="Orbit AI Chat", page_icon="🔮", layout="wide")
init_session()
user = require_auth()
auth_sidebar(user)
app_header("Orbit AI Chat", "Ask Orbit anything. Replies are grounded in your saved chart context.")


def _compact_chart_context(source_data: dict[str, Any]) -> str:
    mode = source_data.get("mode", "unknown")
    lines = [f"mode={mode}"]

    sun_sign = source_data.get("sun_sign")
    moon_sign = source_data.get("moon_sign")
    rising_sign = source_data.get("rising_sign")
    if sun_sign:
        lines.append(f"sun_sign={sun_sign}")
    if moon_sign:
        lines.append(f"moon_sign={moon_sign}")
    if rising_sign:
        lines.append(f"rising_sign={rising_sign}")

    for body in source_data.get("planets", [])[:8]:
        planet = body.get("planet")
        sign = body.get("sign")
        house = body.get("house")
        degree = body.get("degree")
        if planet and sign:
            house_part = f", house={house}" if house else ""
            degree_part = f", degree={degree}" if degree is not None else ""
            lines.append(f"{planet}: sign={sign}{degree_part}{house_part}")

    return "\n".join(lines)


reading_service = ReadingService()
llm = LLMService()

with st.spinner("Loading your chart context..."):
    origin = reading_service.get_or_create_origin_chart(user)

chart_context = _compact_chart_context(origin.source_data)
st.caption("Orbit AI uses your chart context from your Origin Chart. This is interpretive guidance, not deterministic prediction.")

if "orbit_chat_history" not in st.session_state:
    st.session_state.orbit_chat_history = [
        {
            "role": "assistant",
            "content": (
                "I am Orbit. Ask me about relationships, career, timing, or personal patterns, "
                "and I will map it to your chart context."
            ),
        }
    ]

for message in st.session_state.orbit_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask Orbit about your chart...")
if prompt:
    st.session_state.orbit_chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Orbit is reading your chart..."):
            system_prompt = (
                "You are Orbit AI, a psychologically literate astrologer assistant. "
                "Use only the chart context provided. Be direct and practical. "
                "Do not claim certainty about future events. Avoid mystical filler."
            )
            user_prompt = (
                f"Chart context:\n{chart_context}\n\n"
                f"User question:\n{prompt}\n\n"
                "Answer in 2-4 concise paragraphs. Include one actionable next step."
            )
            fallback_text = (
                "I could not reach the live model right now. "
                "From your chart context, focus on one clear next step, one boundary, and one honest conversation this week."
            )
            result = llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                fallback_text=fallback_text,
                temperature=0.45,
                max_tokens=420,
            )
            st.markdown(result.text)
            st.session_state.orbit_chat_history.append({"role": "assistant", "content": result.text})
