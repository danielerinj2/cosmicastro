from __future__ import annotations

from datetime import date

import streamlit as st

from app.constants import ZODIAC_SIGNS
from app.services.reading_service import ReadingService
from app.ui.components import app_header, auth_sidebar, confidence_banner, premium_upgrade_block
from app.ui.session import init_session, require_auth
from app.utils.astro import sun_sign_for_date

st.set_page_config(page_title="Between Us", page_icon="💞", layout="wide")
init_session()
user = require_auth()
auth_sidebar(user)
service = ReadingService()

app_header("Between Us", "Compatibility across six dimensions.")

if not premium_upgrade_block(user, "Between Us"):
    st.stop()

partners = service.repo.list_partner_profiles(user.id)
options = {f"{p.name} ({p.relationship_type or 'partner'})": p.id for p in partners}

selected_partner_id = st.selectbox(
    "Choose existing partner profile",
    options=["None"] + list(options.keys()),
)

partner = None
if selected_partner_id != "None":
    partner = service.repo.get_partner_profile(options[selected_partner_id])

with st.expander("Add new partner profile"):
    with st.form("add_partner_form"):
        name = st.text_input("Name")
        relationship_type = st.selectbox(
            "Relationship type",
            options=["romantic", "friend", "family", "coworker", "other"],
            index=0,
        )
        has_dob = st.checkbox("I know their date of birth", value=False)
        dob = st.date_input("Date of birth", value=date(2000, 1, 1), disabled=not has_dob)
        has_birth_time = st.checkbox("I know their birth time", value=False, disabled=not has_dob)
        birth_time = st.time_input("Birth time", disabled=not has_birth_time)
        birth_location = st.text_input("Birth location", disabled=not has_dob)
        sun_sign = st.selectbox("Sun sign (optional fallback)", options=["Unknown"] + ZODIAC_SIGNS)
        add_partner = st.form_submit_button("Save Partner")

    if add_partner:
        if not name.strip():
            st.error("Partner name is required.")
        else:
            partner = service.repo.create_partner_profile(
                user_id=user.id,
                name=name.strip(),
                dob=dob if has_dob else None,
                birth_time=birth_time.isoformat() if (has_dob and has_birth_time) else None,
                birth_location=birth_location.strip() or None,
                lat=None,
                lng=None,
                timezone=None,
                sun_sign=(sun_sign_for_date(dob) if has_dob else (None if sun_sign == "Unknown" else sun_sign)),
                relationship_type=relationship_type,
            )
            st.success("Partner profile saved. Re-run to select it.")

manual_name = st.text_input("Or run a name-only reflection with:", value="") if partner is None else None

if st.button("Generate Between Us Reading", type="primary"):
    reading = service.get_or_create_between_us(
        user=user,
        partner=partner,
        partner_name=manual_name.strip() if manual_name else None,
    )
    st.session_state["between_us_latest_id"] = reading.id
    st.session_state["between_us_latest_content"] = reading.content
    st.session_state["between_us_latest_mode"] = reading.mode

content = st.session_state.get("between_us_latest_content")
mode = st.session_state.get("between_us_latest_mode")
if content and mode:
    confidence_banner(
        mode,
        full_text="Full synastry mode: highest data precision.",
        light_text="Reduced-data mode: insights are intentionally scoped to available inputs.",
    )
    st.markdown(f"### {content['summary']['headline']}")
    for p in content["summary"]["paragraphs"]:
        st.write(p)
    if content["summary"].get("llm_voice"):
        st.write(content["summary"]["llm_voice"])

    st.subheader("Six Dimensions")
    for dim in content.get("dimensions", []):
        with st.expander(f"{dim['label']} · {dim['score_label']}"):
            if dim.get("astro_basis"):
                st.caption(f"Basis: {dim['astro_basis']}")
            st.write(dim["llm_text"])

    st.subheader("Reflection Prompts")
    for prompt in content.get("reflection_prompts", []):
        st.write(f"- {prompt}")

    for note in content.get("disclaimers", []):
        st.warning(note)
