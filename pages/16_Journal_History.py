from __future__ import annotations

import streamlit as st

from app.repos.supabase_repo import SupabaseRepository
from app.ui.components import app_header, auth_sidebar
from app.ui.session import init_session, require_auth

st.set_page_config(page_title="Journal / History", page_icon="📓", layout="wide")
init_session()
user = require_auth()
auth_sidebar(user)
repo = SupabaseRepository()

app_header("Journal / Reading History", "All readings and reactions in one place.")

readings = repo.list_readings(user.id, limit=100)
reactions = repo.list_reactions(user.id, limit=200)

st.subheader("Reading Timeline")
if not readings:
    st.info("No readings yet. Generate one from Home, Origin Chart, Between Us, or Yearly Chart.")
else:
    for reading in readings:
        with st.expander(f"{reading.type} · {reading.mode} · {reading.created_at.date().isoformat()}"):
            summary = reading.content.get("summary", {})
            st.write(summary.get("headline", "No headline"))
            if summary.get("llm_voice"):
                st.write(summary["llm_voice"])
            if reading.content.get("disclaimers"):
                for note in reading.content["disclaimers"]:
                    st.caption(note)

st.divider()
st.subheader("Reactions")
if not reactions:
    st.info("No reactions yet.")
else:
    for item in reactions:
        reaction = item.get("reaction", "")
        journal_text = item.get("journal_text")
        created_at = item.get("created_at", "")
        st.write(f"- `{created_at}` · **{reaction}**")
        if journal_text:
            st.caption(journal_text)
