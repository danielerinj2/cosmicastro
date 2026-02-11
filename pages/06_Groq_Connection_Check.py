from __future__ import annotations

import streamlit as st

from app.config import AppConfig
from app.services.llm_service import LLMService
from app.ui.components import auth_sidebar
from app.ui.session import get_current_user, init_session

st.set_page_config(page_title="Groq Connection Check", page_icon="🤖", layout="wide")
init_session()
auth_sidebar(get_current_user())

st.title("Groq Connection Check")
st.caption("Validate key and model via a small completion request")

config = AppConfig.from_env()
missing = config.missing_groq_env()
if missing:
    st.error(f"Missing env vars: {', '.join(missing)}")
    st.stop()

st.success("Groq env vars detected.")
st.code(
    f"LLM_PROVIDER={config.llm_provider}\nGROQ_MODEL={config.groq_model}",
    language="bash",
)

if st.button("Run Live Groq Check", type="primary"):
    service = LLMService()
    result = service.generate(
        system_prompt="You are concise.",
        user_prompt="Reply with exactly GROQ_OK",
        fallback_text="GROQ_FALLBACK",
        temperature=0,
        max_tokens=6,
    )
    if result.ok:
        st.success("Groq API call succeeded.")
    else:
        st.error(result.message)
    st.write(f"Response: `{result.text.strip()}`")
