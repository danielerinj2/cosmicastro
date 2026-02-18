from __future__ import annotations

import os
import re
from datetime import time

import streamlit as st
from streamlit.components.v1 import html as components_html

from app.constants import LAUNCH_TRUST_MESSAGE
from app.domain.models import User
from app.services.stripe_service import StripeService

_AMPM_TIME_RE = re.compile(r"^\s*(1[0-2]|0?[1-9]):([0-5][0-9])\s*([AaPp][Mm])\s*$")
UNICORN_PROJECT_ID = "prCymyNE9DjMip7xfyZf"
UNICORN_SDK_URL = (
    "https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v2.0.5/dist/unicornStudio.umd.js"
)


def app_header(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def auth_sidebar(user: User | None) -> None:
    theme_preference = user.theme_preference if user else "dark"
    _apply_theme(theme_preference)
    with st.sidebar:
        st.page_link("pages/12_Daily_Horoscope.py", label="Daily Horoscope")
        st.page_link("pages/11_Origin_Chart.py", label="Origin Chart")
        st.page_link("pages/13_Between_Us.py", label="Between Us")
        st.page_link("pages/14_Yearly_Chart.py", label="Yearly Chart")
        st.page_link("pages/17_Orbit_AI_Chat.py", label="Orbit AI Chat")
        st.page_link("pages/15_Settings_Profile.py", label="Settings")
        st.page_link("pages/09_Log_Out.py", label="Log out")
        st.markdown(f"<p class='sidebar-trust'>{LAUNCH_TRUST_MESSAGE}</p>", unsafe_allow_html=True)


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


def render_unicorn_scene(height: int = 400) -> None:
    container_height = max(int(height), 280)
    snippet = f"""
<div id="unicorn-container" style="width:100%; height:{container_height}px;"></div>
<script src="{UNICORN_SDK_URL}"></script>
<script>
(async function () {{
  try {{
    if (!window.UnicornStudio) return;
    await window.UnicornStudio.addScene({{
      elementId: "unicorn-container",
      projectId: "{UNICORN_PROJECT_ID}",
      scale: 1,
      dpi: 1.5,
      fps: 60,
      lazyLoad: true,
      production: true
    }});
  }} catch (e) {{
    // Silent fail with placeholder text below.
  }}
}})();
</script>
<noscript>Enable JavaScript to view the interactive scene.</noscript>
"""
    components_html(snippet, height=container_height, scrolling=False)


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
        sidebar_link_bg = "#e2e8f0"
        sidebar_link_hover_bg = "#dbeafe"
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
        sidebar_link_bg = "#1f2937"
        sidebar_link_hover_bg = "#273244"

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;500&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
  font-family: "Sora", sans-serif !important;
  font-weight: 300 !important;
}}

h1, h2, h3, h4, h5, h6,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6 {{
  font-family: "Sora", sans-serif !important;
  font-weight: 500 !important;
}}

button, input, textarea, select, label, p, span, li, small, div {{
  font-family: "Sora", sans-serif !important;
  font-weight: 300 !important;
}}

[data-testid="stAppViewContainer"] {{
  background: {app_bg};
  color: {text_color};
}}
[data-testid="stHeader"] {{
  background: {app_bg};
}}
[data-testid="stHeader"] button,
[data-testid="stHeader"] [role="button"],
[data-testid="collapsedControl"] {{
  color: {text_color} !important;
  background: transparent !important;
  border: 1px solid {border_color} !important;
}}
[data-testid="stHeader"] button:hover,
[data-testid="stHeader"] [role="button"]:hover,
[data-testid="collapsedControl"]:hover {{
  background: {card_bg} !important;
}}
[data-testid="stSidebar"] {{
  background: {panel_bg};
}}
[data-testid="stSidebar"] * {{
  color: {text_color} !important;
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a *,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"],
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] * {{
  color: {text_color} !important;
  opacity: 1 !important;
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
  border-radius: 0 !important;
  border: none !important;
  background: transparent !important;
  padding: 0 !important;
  margin: 0 0 10px 0 !important;
  text-decoration: none !important;
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
  background: transparent !important;
  border: none !important;
  text-decoration: underline !important;
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-selected="true"] {{
  background: transparent !important;
  border: none !important;
  font-weight: 500 !important;
  text-decoration: underline !important;
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-disabled="true"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a:disabled {{
  opacity: 1 !important;
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
[data-testid="stSidebar"] .stFormSubmitButton > button {{
  background: {button_bg} !important;
  color: {button_fg} !important;
  border: 1px solid {button_border} !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  filter: brightness(0.98);
}}
[data-testid="stSidebar"] .stFormSubmitButton > button:hover {{
  filter: brightness(0.98);
}}
[data-testid="stAppViewContainer"] .stButton > button,
[data-testid="stAppViewContainer"] .stFormSubmitButton > button {{
  background: {button_bg} !important;
  color: {button_fg} !important;
  border: 1px solid {button_border} !important;
}}
[data-testid="stAppViewContainer"] .stButton > button:hover,
[data-testid="stAppViewContainer"] .stFormSubmitButton > button:hover {{
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
.sidebar-trust {{
  margin-top: 10px;
  font-size: 0.92rem;
  line-height: 1.45;
  color: {muted_text} !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )
