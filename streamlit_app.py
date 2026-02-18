from __future__ import annotations

import re
from html import escape, unescape
from typing import Any

import streamlit as st

from app.content.homepage_content import DEFAULT_HOMEPAGE_CONTENT, load_homepage_content
from app.services.auth_service import AuthService
from app.ui.components import auth_sidebar
from app.ui.session import get_current_user, init_session

st.set_page_config(
    page_title="Discover Your Cosmic Self",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
try:
    auth = AuthService()
    user = get_current_user()
except Exception as exc:
    auth = None
    user = None
    st.error("App configuration is incomplete. Please check Streamlit Cloud Secrets.")
    st.code(str(exc))
    st.stop()

auth_sidebar(user)

params = st.query_params


def _query_value(key: str) -> str | None:
    value = params.get(key)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any, fallback: str) -> str:
    raw = fallback if value is None else str(value)
    raw = unescape(raw)
    # Guard against accidentally saved HTML snippets showing up as literal text.
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = " ".join(raw.split())
    return escape(raw)


def _looks_like_markup(text: str) -> bool:
    lowered = unescape(text).lower()
    return any(token in lowered for token in ("<div", "<h", "<p", "orbit-card", "orbit-step", "&lt;div"))


# Backward + forward compatible token keys.
verify_token = _query_value("vt") or _query_value("verify_token")
reset_token = _query_value("rt") or _query_value("reset_token") or _query_value("token")

if verify_token:
    result = auth.verify_email(verify_token)
    if result.ok:
        st.success(result.message)
    else:
        st.error(result.message)
    st.query_params.clear()

if reset_token:
    st.subheader("Reset Password")
    with st.form("reset_via_link_form"):
        new_password = st.text_input("New password", type="password")
        new_password_confirm = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Reset Password")

    if submitted:
        if not new_password or new_password != new_password_confirm:
            st.error("Passwords must match.")
        else:
            result = auth.reset_password(token_value=reset_token, new_password=new_password)
            if result.ok:
                st.success(result.message)
                st.query_params.clear()
            else:
                st.error(result.message)

daily_target = "pages/12_Daily_Horoscope.py" if user else "pages/04_Auth_Sign_In.py"
chat_target = "pages/17_Orbit_AI_Chat.py" if user else "pages/04_Auth_Sign_In.py"
origin_target = "pages/11_Origin_Chart.py" if user else "pages/04_Auth_Sign_In.py"
between_target = "pages/13_Between_Us.py" if user else "pages/04_Auth_Sign_In.py"
yearly_target = "pages/14_Yearly_Chart.py" if user else "pages/04_Auth_Sign_In.py"

homepage_content = load_homepage_content()

hero = _as_dict(homepage_content.get("hero"))
hero_default = _as_dict(DEFAULT_HOMEPAGE_CONTENT.get("hero"))
hero_title = _safe_text(hero.get("title"), str(hero_default.get("title", "Orbit AI")))
hero_cta = str(hero.get("cta_text") or hero_default.get("cta_text") or "Get Your Daily Prediction")

intro = _as_dict(homepage_content.get("intro"))
intro_default = _as_dict(DEFAULT_HOMEPAGE_CONTENT.get("intro"))
intro_p1 = _safe_text(intro.get("paragraph_1"), str(intro_default.get("paragraph_1", "")))
intro_p2 = _safe_text(intro.get("paragraph_2"), str(intro_default.get("paragraph_2", "")))
intro_punch = _safe_text(intro.get("punch_line"), str(intro_default.get("punch_line", "")))

inside_orbit_heading = "Inside Orbit AI"
inside_orbit_cards = [
    {
        "title": "Give us three facts about your birth",
        "body": (
            "Date. Time. Place. That's it. From those three data points, we map the exact sky above you "
            "the moment you arrived. No quizzes. No personality tests. No guessing."
        ),
    },
    {
        "title": "Get a reading that couldn't belong to anyone else",
        "body": (
            "Most horoscopes are written for one-twelfth of the human population at a time. "
            "Yours is written for you."
        ),
    },
    {
        "title": "Still Curious? I'm on speed dial",
        "body": (
            "Career crossroads. A relationship that doesn't add up. That restless feeling you can't explain. "
            "Talk to Orbit AI the way you'd talk to someone who already knows your whole story; because it does."
        ),
    },
]

how_cards_html_parts: list[str] = []
for card in inside_orbit_cards:
    title = _safe_text(card.get("title"), "")
    description = _safe_text(card.get("body"), "")
    how_cards_html_parts.append(
        "<div class=\"orbit-card\">"
        f"<h3>{title}</h3>"
        f"<p>{description}</p>"
        "</div>"
    )
how_cards_html = "".join(how_cards_html_parts)

daily_feature = _as_dict(homepage_content.get("daily_feature"))
daily_default = _as_dict(DEFAULT_HOMEPAGE_CONTENT.get("daily_feature"))
daily_label = _safe_text(daily_feature.get("label"), str(daily_default.get("label", "DAILY HOROSCOPE")))
daily_title = _safe_text(daily_feature.get("title"), str(daily_default.get("title", "")))
daily_p1 = _safe_text(
    "Calibrated to the sky. What's active in your chart today. What deserves restraint and what deserves action.",
    "",
)
daily_tag = _safe_text(daily_feature.get("tagline"), str(daily_default.get("tagline", "")))

birth_feature = _as_dict(homepage_content.get("birth_chart_feature"))
birth_default = _as_dict(DEFAULT_HOMEPAGE_CONTENT.get("birth_chart_feature"))
birth_label = _safe_text(birth_feature.get("label"), str(birth_default.get("label", "BIRTH CHART")))
birth_title = _safe_text(birth_feature.get("title"), str(birth_default.get("title", "")))
birth_p1 = _safe_text(
    "A complete analysis of your natal chart; every planet, every house, every major aspect; interpreted as a coherent pattern. "
    "Orbit doesn't isolate placements; it examines how they interact to reveal recurring dynamics in your personality, relationships, and stress responses.",
    "",
)
birth_p2 = ""
birth_tag = _safe_text(birth_feature.get("tagline"), str(birth_default.get("tagline", "")))

compat_feature = _as_dict(homepage_content.get("compatibility_feature"))
compat_default = _as_dict(DEFAULT_HOMEPAGE_CONTENT.get("compatibility_feature"))
compat_label = _safe_text(compat_feature.get("label"), str(compat_default.get("label", "COMPATIBILITY")))
compat_title = _safe_text(compat_feature.get("title"), str(compat_default.get("title", "")))
compat_p1 = _safe_text(compat_feature.get("paragraph_1"), str(compat_default.get("paragraph_1", "")))
compat_p2 = _safe_text(compat_feature.get("paragraph_2"), str(compat_default.get("paragraph_2", "")))
compat_tag = _safe_text(compat_feature.get("tagline"), str(compat_default.get("tagline", "")))

chat_feature = _as_dict(homepage_content.get("chatbot_feature"))
chat_default = _as_dict(DEFAULT_HOMEPAGE_CONTENT.get("chatbot_feature"))
chat_title = _safe_text("Ask Orbit AI", "")
chat_subheading = _safe_text("Real-time answers.", "")
chat_intro = _safe_text(
    "The thing you're overthinking at 2 a.m. You bring the question. "
    "No scheduling. No waiting. An astrologer in your pocket. 24/7",
    "",
)
chat_messages = _as_list(chat_feature.get("messages")) or _as_list(chat_default.get("messages"))
chat_rows: list[str] = []
for message in chat_messages[:8]:
    msg = _as_dict(message)
    role = str(msg.get("role", "user")).lower().strip()
    text = _safe_text(msg.get("text"), "")
    if role == "assistant":
        chat_rows.append(
            "<div class=\"orbit-chat-row assistant\">"
            "<div class=\"orbit-assistant-wrap\">"
            "<span class=\"orbit-ai-icon\">O</span>"
            f"<div class=\"orbit-bubble assistant\">{text}</div>"
            "</div>"
            "</div>"
        )
    else:
        chat_rows.append(
            "<div class=\"orbit-chat-row user\">"
            f"<div class=\"orbit-bubble user\">{text}</div>"
            "</div>"
        )
chat_html = "".join(chat_rows)

yearly_feature = _as_dict(homepage_content.get("yearly_feature"))
yearly_default = _as_dict(DEFAULT_HOMEPAGE_CONTENT.get("yearly_feature"))
yearly_title = _safe_text("YEARLY FORECAST", "")
yearly_subheading = _safe_text("A month-by-month breakdown.", "")
yearly_p1 = _safe_text(
    "Most people fail because they push at the wrong time. "
    "There are months built for expansion. Months built for consolidation. "
    "This forecast shows you the pattern before it plays out.",
    "",
)

social = _as_dict(homepage_content.get("social_proof"))
social_default = _as_dict(DEFAULT_HOMEPAGE_CONTENT.get("social_proof"))
social_title = _safe_text(social.get("title"), str(social_default.get("title", "What People Are Saying")))
social_line = _safe_text("We're new here. You're early. We're looking forward to what you'll say.", "")
social_placeholder = _safe_text(
    social.get("placeholder_text"),
    str(social_default.get("placeholder_text", "Testimonials coming soon")),
)

st.markdown(
    """
<style>
[data-testid="stAppViewContainer"] .main .block-container {
  max-width: 100%;
  padding: 0;
}
[data-testid="stAppViewContainer"] {
  background: #0A0A0F;
}
.orbit-root {
  background: #0A0A0F;
  color: #FFFFFF;
}
.orbit-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 24px;
}
.orbit-h1,
.orbit-h2,
.orbit-h3 {
  line-height: 1.2;
  color: #FFFFFF;
  font-weight: 500;
}
.orbit-body {
  line-height: 1.65;
  color: #9999AA;
  font-weight: 300;
}
.orbit-label {
  text-transform: uppercase;
  letter-spacing: 3px;
  color: #8B5CF6;
  font-size: 13px;
  font-weight: 500;
  text-align: center;
  margin: 0 0 16px 0;
}
.hero-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0 20px 0 20px;
  margin-top: -8px;
}
.hero-title {
  font-size: 120px;
  margin-bottom: 24px;
  font-weight: 500;
  color: #FFFFFF;
  line-height: 1.2;
}
.hero-description {
  max-width: 760px;
  margin: 0 auto;
  line-height: 1.62;
  color: #9999AA;
  font-size: 18px;
}
.punchline {
  display: block;
  margin-top: 20px;
  font-weight: 400;
  color: #FFFFFF;
}
[data-testid="stAppViewContainer"] .stButton {
  display: block;
  width: 100%;
}
[data-testid="stAppViewContainer"] .stButton > button[kind="primary"] {
  font-size: 16px !important;
  font-weight: 500 !important;
  background: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #FFFFFF !important;
  border-radius: 56px !important;
  padding: 9px 24px !important;
  min-width: 320px !important;
  opacity: 1 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin-left: auto !important;
  margin-right: auto !important;
  text-align: center !important;
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: clip !important;
}
[data-testid="stAppViewContainer"] .stButton > button[kind="primary"] *,
[data-testid="stAppViewContainer"] .stButton > button[kind="primary"] span,
[data-testid="stAppViewContainer"] .stButton > button[kind="primary"] p {
  color: #000000 !important;
  opacity: 1 !important;
  -webkit-text-fill-color: #000000 !important;
}
[data-testid="stAppViewContainer"] .stButton > button[kind="primary"]:disabled,
[data-testid="stAppViewContainer"] .stButton > button[kind="primary"]:disabled * {
  color: #000000 !important;
  opacity: 1 !important;
  -webkit-text-fill-color: #000000 !important;
}
[data-testid="stAppViewContainer"] .stButton > button[kind="primary"]:hover {
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.20), 0 0 24px rgba(139, 92, 246, 0.35) !important;
}
.orbit-how-section {
  padding: 0;
}
.orbit-how-panel {
  background: #111118;
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 14px;
}
.orbit-how-heading {
  font-size: 44px;
  font-weight: 500;
  color: #FFFFFF;
  line-height: 1.2;
  text-align: center;
  margin: 0;
}
.orbit-how-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
  align-items: stretch;
}
.orbit-card {
  background: #161622;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 36px 28px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  text-align: center;
}
.orbit-card h3 {
  font-size: 27px;
  margin: 0 0 16px 0;
  font-weight: 500;
  color: #FFFFFF;
  line-height: 1.3;
  text-align: center;
}
.orbit-card p {
  font-size: 16px;
  margin: 0;
  line-height: 1.65;
  color: #9999AA;
  font-weight: 300;
  text-align: center;
}

/* ── Feature sections ── */
.orbit-feature-section {
  padding: 56px 0;
  text-align: center;
}
.orbit-feature-daily {
  padding-top: 36px;
  padding-bottom: 24px;
}
.orbit-feature-birth {
  padding-top: 36px;
  padding-bottom: 24px;
}
.orbit-feature-section .orbit-copy {
  max-width: 720px;
  margin: 0 auto;
}
.orbit-feature-section .orbit-h2 {
  font-size: 36px;
  margin: 16px 0 0 0;
}
.orbit-feature-section .orbit-body {
  font-size: 17px;
  margin: 24px 0 0 0;
}
.orbit-feature-section .orbit-body + .orbit-body {
  margin-top: 16px;
}
.orbit-feature-section .orbit-tagline {
  margin-top: 16px;
  color: #FFFFFF;
  font-weight: 500;
  font-size: 18px;
}
.orbit-subheading {
  margin: 10px 0 0 0;
  font-size: 18px;
  color: #9999AA;
  font-weight: 300;
  line-height: 1.55;
}
.orbit-feature-daily .orbit-label {
  margin: 0 0 24px 0;
}
.orbit-feature-daily .orbit-h2 {
  margin: 0;
}
.orbit-feature-daily .orbit-body {
  margin: 24px 0 0 0;
}
.orbit-feature-birth .orbit-label {
  margin: 0 0 24px 0;
}
.orbit-feature-birth .orbit-h2 {
  margin: 0;
}
.orbit-feature-birth .orbit-body {
  margin: 24px 0 0 0;
}

/* ── Chat section ── */
.orbit-chat-section {
  padding: 56px 0;
  text-align: center;
}
.orbit-chat-section .orbit-copy {
  max-width: 640px;
  margin: 0 auto;
}
.orbit-chat-section .orbit-h2 {
  font-size: 40px;
  margin: 0;
}
.orbit-chat-section .orbit-body {
  font-size: 17px;
  margin: 18px auto 0 auto;
}
.orbit-chat-card {
  margin: 28px auto 0 auto;
  max-width: 600px;
  background: #111118;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 32px;
  text-align: left;
}
.orbit-chat-row {
  display: flex;
  margin-bottom: 16px;
}
.orbit-chat-row:last-child {
  margin-bottom: 0;
}
.orbit-chat-row.user {
  justify-content: flex-end;
}
.orbit-chat-row.assistant {
  justify-content: flex-start;
}
.orbit-assistant-wrap {
  display: flex;
  align-items: flex-start;
}
.orbit-ai-icon {
  width: 12px;
  height: 12px;
  min-width: 12px;
  border-radius: 50%;
  background: #8B5CF6;
  color: #FFFFFF;
  font-size: 8px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  margin-top: 6px;
}
.orbit-bubble {
  max-width: 88%;
  padding: 14px 20px;
  font-size: 15px;
  line-height: 1.65;
  font-weight: 300;
}
.orbit-bubble.user {
  background: #1E1E2E;
  color: #FFFFFF;
  border-radius: 16px 16px 4px 16px;
}
.orbit-bubble.assistant {
  background: rgba(139, 92, 246, 0.125);
  color: #CCCCDD;
  border-radius: 16px 16px 16px 4px;
}
.orbit-chat-closing {
  max-width: 600px;
  margin: 20px auto 0 auto;
  text-align: center;
  font-size: 16px;
}

/* ── Social proof ── */
.orbit-social-section {
  background: #111118;
  padding: 56px 0;
  text-align: center;
}
.orbit-social-section .orbit-h2 {
  font-size: 36px;
  margin: 0;
}
.orbit-social-section .orbit-body {
  font-size: 17px;
  margin-top: 20px;
}
.orbit-testimonial-placeholder {
  min-height: 200px;
  margin-top: 34px;
  border: 1px dashed rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.30);
  font-size: 16px;
  font-weight: 300;
}

/* ── Closing ── */
.orbit-closing-section {
  padding-top: 72px;
  padding-bottom: 88px;
  text-align: center;
}
.orbit-closing-section .orbit-h2 {
  font-size: 40px;
  margin: 0;
}
.orbit-closing-section .orbit-subheadline {
  margin-top: 16px;
  font-size: 20px;
  color: #9999AA;
  font-weight: 300;
}

@media (max-width: 980px) {
  .hero-title {
    font-size: 58px;
  }
  .hero-description {
    max-width: 92vw;
    font-size: 17px;
  }
  [data-testid="stAppViewContainer"] .stButton > button[kind="primary"] {
    min-width: 280px !important;
  }
  .orbit-how-panel {
    padding: 10px;
  }
  .orbit-how-heading {
    font-size: 34px;
  }
  .orbit-how-grid {
    grid-template-columns: 1fr;
  }
  .orbit-card h3 {
    font-size: 24px;
  }
}
.orbit-root a[aria-label*="Anchor"],
.orbit-root a[aria-label*="anchor"],
.orbit-root a[aria-label*="link"],
.orbit-root .anchor-link,
.orbit-root h1 a,
.orbit-root h2 a,
.orbit-root h3 a,
.hero-title a,
.hero-title + a,
.hero-section a[aria-label*="link"],
.hero-section .anchor-link {
  display: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="orbit-root">
  <section class="hero-section">
    <div class="orbit-container">
      <h1 class="hero-title">{hero_title}</h1>
      <p class="hero-description">
        Your horoscope said something about &#x27;new beginnings&#x27; and &#x27;trusting the process.&#x27; Cool. So did everyone else&#x27;s. That&#x27;s like diagnosing someone by looking at their shoes.
        <span class="punchline">The universe doesn&#x27;t deal in vague predictions. Neither do we.</span>
      </p>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
hero_col_left, hero_col_center, hero_col_right = st.columns([1, 1, 1])
with hero_col_center:
    if st.button(hero_cta, key="hero_daily_prediction", type="primary"):
        st.switch_page(daily_target)
st.markdown("<div style='height:0;'></div>", unsafe_allow_html=True)


def _render_center_cta(label: str, key: str, target: str) -> None:
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        if st.button(label, key=key, type="primary"):
            st.switch_page(target)
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)


st.markdown(
    f"""
<div class="orbit-root">
  <section class="orbit-how-section">
    <div class="orbit-container">
      <div class="orbit-how-panel">
        <h2 class="orbit-how-heading">{inside_orbit_heading}</h2>
        <div class="orbit-how-grid">
          {how_cards_html}
        </div>
      </div>
    </div>
  </section>

  <section class="orbit-feature-section orbit-feature-daily">
    <div class="orbit-container orbit-copy">
      <p class="orbit-label">{daily_label}</p>
      <h2 class="orbit-h2">{daily_title}</h2>
      <p class="orbit-body">{daily_p1}</p>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)

_render_center_cta("Get Today's Reading", "daily_section_cta", daily_target)

st.markdown(
    f"""
<div class="orbit-root">

  <section class="orbit-feature-section orbit-feature-birth">
    <div class="orbit-container orbit-copy">
      <p class="orbit-label">{birth_label}</p>
      <h2 class="orbit-h2">{birth_title}</h2>
      <p class="orbit-body">{birth_p1}</p>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)

_render_center_cta("Get My Birth Chart", "birth_section_cta", origin_target)

st.markdown(
    f"""
<div class="orbit-root">
  <section class="orbit-feature-section">
    <div class="orbit-container orbit-copy">
      <p class="orbit-label">{compat_label}</p>
      <h2 class="orbit-h2">{compat_title}</h2>
      <p class="orbit-body">{compat_p1}</p>
      <p class="orbit-body">{compat_p2}</p>
      <p class="orbit-tagline">{compat_tag}</p>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)

_render_center_cta("Check Compatibility", "compat_section_cta", between_target)

st.markdown(
    f"""
<div class="orbit-root">
  <section class="orbit-chat-section">
    <div class="orbit-container">
      <div class="orbit-copy">
        <h2 class="orbit-h2">{chat_title}</h2>
        <p class="orbit-subheading">{chat_subheading}</p>
        <p class="orbit-body">{chat_intro}</p>
      </div>
      <div class="orbit-chat-card">
        {chat_html}
      </div>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)

_render_center_cta("Start the Conversation", "chat_section_cta", chat_target)

st.markdown(
    f"""
<div class="orbit-root">
  <section class="orbit-feature-section">
    <div class="orbit-container orbit-copy">
      <h2 class="orbit-h2">{yearly_title}</h2>
      <p class="orbit-subheading">{yearly_subheading}</p>
      <p class="orbit-body">{yearly_p1}</p>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)

_render_center_cta("Map My Year", "yearly_section_cta", yearly_target)

st.markdown(
    f"""
<div class="orbit-root">
  <section class="orbit-social-section">
    <div class="orbit-container orbit-copy">
      <h2 class="orbit-h2">{social_title}</h2>
      <p class="orbit-body">{social_line}</p>
      <div class="orbit-testimonial-placeholder">{social_placeholder}</div>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)
