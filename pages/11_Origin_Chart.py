from __future__ import annotations

import streamlit as st

from app.services.reading_service import ReadingService
from app.services.stripe_service import StripeService
from app.ui.components import app_header, auth_sidebar, confidence_banner, premium_upgrade_block
from app.ui.session import init_session, require_auth

st.set_page_config(page_title="Origin Chart", page_icon="🪐", layout="wide", initial_sidebar_state="collapsed")
init_session()
user = require_auth()
auth_sidebar(user)
service = ReadingService()
stripe = StripeService()

app_header("Your Origin Chart", "The most honest mirror you'll ever look into.")
reading = service.get_or_create_origin_chart(user)
mode = reading.mode

confidence_banner(
    mode,
    full_text="This is a full chart: time/place provided. Rising sign and houses included.",
    light_text="Birth-date-only mode: signs are available; Rising sign and houses are hidden until time/place are added.",
)

summary = reading.content.get("summary", {})
st.subheader("In One Glance")
st.markdown(f"### {summary.get('headline', 'Your chart snapshot')}")
for paragraph in summary.get("paragraphs", []):
    st.write(paragraph)
is_premium = stripe.user_has_active_premium(user)
if summary.get("llm_voice") and is_premium:
    st.write(summary["llm_voice"])
elif not is_premium:
    st.caption("Full synthesized interpretation is part of Premium.")

st.divider()
st.subheader("Your Planetary Placements")
placements = reading.content.get("placements", [])
visible_placements = placements if is_premium else placements[:3]
for placement in visible_placements:
    title = f"{placement['planet']} in {placement['sign']}"
    if mode == "full" and placement.get("house"):
        title += f" · {placement.get('degree', '')}° · House {placement['house']}"
    elif placement.get("degree") is not None:
        title += f" · {placement.get('degree')}°"
    with st.expander(title):
        if is_premium:
            st.write(placement.get("llm_text", "No interpretation available yet."))
        else:
            st.write("Placement details unlocked with Premium.")

if reading.content.get("aspects") and is_premium:
    st.divider()
    st.subheader("Major Aspects")
    for aspect in reading.content["aspects"]:
        st.write(f"- {aspect['a']} {aspect['aspect']} {aspect['b']} (orb {aspect['orb']}°)")

if reading.content.get("disclaimers"):
    st.divider()
    st.subheader("Reading Notes")
    for note in reading.content["disclaimers"]:
        st.write(f"- {note}")

if not is_premium:
    premium_upgrade_block(user, "Origin Chart Full Interpretation")
