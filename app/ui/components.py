from __future__ import annotations

import os
import re
from datetime import time

import streamlit as st

from app.constants import LAUNCH_TRUST_MESSAGE
from app.domain.models import User
from app.services.stripe_service import StripeService
from app.ui.session import logout_user

_AMPM_TIME_RE = re.compile(r"^\s*(1[0-2]|0?[1-9]):([0-5][0-9])\s*([AaPp][Mm])\s*$")


def app_header(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def auth_sidebar(user: User | None) -> None:
    theme_preference = user.theme_preference if user else "dark"
    _apply_theme(theme_preference)
    with st.sidebar:
        st.markdown("## Discover Your Cosmic Self")
        if user:
            st.write(f"Signed in as **{user.first_name}**")
            st.write(f"Plan: {user.subscription_tier.title()}")
            if st.button("Log out"):
                logout_user()
                st.rerun()
        else:
            st.write("Not signed in.")
        st.divider()
        st.info(LAUNCH_TRUST_MESSAGE)


def confidence_banner(mode: str, full_text: str, light_text: str) -> None:
    if mode in {"full", "full_profection", "full_synastry"}:
        st.success(full_text)
    else:
        st.warning(light_text)


def premium_upgrade_block(user: User, feature_name: str) -> bool:
    # Stripe is scaffolded but optional for now. Keep product flows usable unless explicitly enabled.
    enforce_gating = os.getenv("ENABLE_PREMIUM_GATING", "false").strip().lower() == "true"
    if not enforce_gating:
        return True

    stripe = StripeService()
    if stripe.user_has_active_premium(user):
        return True

    st.warning(f"`{feature_name}` is part of Premium.")
    st.caption("Upgrade to unlock unlimited compatibility, yearly chart depth, and full interpretation access.")

    if not stripe.configured():
        st.info("Stripe is not configured yet. Add Stripe env vars to enable checkout links.")
        return False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Upgrade Monthly ($4.99)", key=f"upgrade_monthly_{feature_name}"):
            result = stripe.create_checkout_session(user, plan="monthly")
            if result.ok and result.url:
                st.link_button("Open Stripe Checkout (Monthly)", result.url)
            else:
                st.error(result.message)
    with col2:
        if st.button("Upgrade Yearly ($29.99)", key=f"upgrade_yearly_{feature_name}"):
            result = stripe.create_checkout_session(user, plan="yearly")
            if result.ok and result.url:
                st.link_button("Open Stripe Checkout (Yearly)", result.url)
            else:
                st.error(result.message)
    return False


def format_time_ampm(value: time | None) -> str:
    if value is None:
        return ""
    hour = value.hour % 12 or 12
    meridiem = "AM" if value.hour < 12 else "PM"
    return f"{hour:02d}:{value.minute:02d} {meridiem}"


def parse_time_ampm(value: str) -> time | None:
    raw = value.strip()
    if not raw:
        return None
    match = _AMPM_TIME_RE.match(raw)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    meridiem = match.group(3).upper()
    if meridiem == "AM":
        hour_24 = 0 if hour == 12 else hour
    else:
        hour_24 = 12 if hour == 12 else hour + 12
    return time(hour=hour_24, minute=minute)


def _apply_theme(theme_preference: str) -> None:
    theme = "light" if theme_preference == "light" else "dark"
    if theme == "light":
        app_bg = "#f5f7fb"
        panel_bg = "#edf2f7"
        card_bg = "#ffffff"
        text_color = "#0f172a"
        border_color = "#cbd5e1"
        muted_text = "#475569"
        button_bg = "#ffffff"
        button_fg = "#0f172a"
        button_border = "#94a3b8"
        code_bg = "#e2e8f0"
        code_fg = "#0f172a"
    else:
        app_bg = "#0f172a"
        panel_bg = "#111827"
        card_bg = "#1f2937"
        text_color = "#e5e7eb"
        border_color = "#374151"
        muted_text = "#9ca3af"
        button_bg = "#374151"
        button_fg = "#e5e7eb"
        button_border = "#4b5563"
        code_bg = "#0b1220"
        code_fg = "#e5e7eb"

    st.markdown(
        f"""
<style>
[data-testid="stAppViewContainer"] {{
  background: {app_bg};
  color: {text_color};
}}
[data-testid="stHeader"] {{
  background: {app_bg};
}}
[data-testid="stSidebar"] {{
  background: {panel_bg};
}}
[data-testid="stSidebar"] * {{
  color: {text_color} !important;
}}
[data-testid="stSidebar"] code {{
  background: {code_bg} !important;
  color: {code_fg} !important;
  border: 1px solid {border_color};
}}
[data-testid="stSidebar"] .stButton > button {{
  background: {button_bg} !important;
  color: {button_fg} !important;
  border: 1px solid {button_border} !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  filter: brightness(0.98);
}}
[data-testid="stMarkdownContainer"], .stCaption, label, p, h1, h2, h3, h4, h5, h6 {{
  color: {text_color} !important;
}}
.stAlert {{
  border: 1px solid {border_color};
}}
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input {{
  background: {card_bg};
  color: {text_color};
  border: 1px solid {border_color};
}}
[data-baseweb="select"] > div {{
  background: {card_bg};
  color: {text_color};
  border-color: {border_color};
}}
.stRadio [role="radiogroup"] label, .stCheckbox label {{
  color: {text_color} !important;
}}
.stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] {{
  color: {muted_text};
}}
</style>
        """,
        unsafe_allow_html=True,
    )
