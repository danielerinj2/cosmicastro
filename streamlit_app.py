from __future__ import annotations

import json
from html import escape

import streamlit as st

from app.content.homepage_content import (
    DEFAULT_HOMEPAGE_CONTENT,
    load_homepage_content,
    save_homepage_content,
)
from app.services.auth_service import AuthService
from app.ui.components import auth_sidebar
from app.ui.session import get_current_user, init_session

st.set_page_config(
    page_title="Discover Your Cosmic Self",
    page_icon="✨",
    layout="wide",
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
homepage_content = load_homepage_content()

if user:
    with st.expander("Edit Homepage Content", expanded=False):
        st.caption(
            "Manual editor for homepage copy. Edit JSON and click Save. "
            "Changes are saved to app/content/homepage_content.json."
        )
        raw_json = st.text_area(
            "Homepage Content JSON",
            value=json.dumps(homepage_content, ensure_ascii=True, indent=2),
            height=420,
            key="homepage_editor_json",
        )
        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("Save Homepage Content", key="save_homepage_content"):
                try:
                    parsed = json.loads(raw_json)
                    if not isinstance(parsed, dict):
                        raise ValueError("JSON root must be an object.")
                    save_homepage_content(parsed)
                    st.success("Homepage content saved.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not save content: {exc}")
        with col_reset:
            if st.button("Reset To Default Content", key="reset_homepage_content"):
                save_homepage_content(DEFAULT_HOMEPAGE_CONTENT)
                st.success("Homepage content reset to defaults.")
                st.rerun()

hero = homepage_content.get("hero", {})
hero_title = escape(str(hero.get("title", DEFAULT_HOMEPAGE_CONTENT["hero"]["title"])))
hero_subtitle = escape(str(hero.get("subtitle", DEFAULT_HOMEPAGE_CONTENT["hero"]["subtitle"])))
hero_cta = str(hero.get("cta_text", DEFAULT_HOMEPAGE_CONTENT["hero"]["cta_text"]))

how_items = homepage_content.get("how_it_works", DEFAULT_HOMEPAGE_CONTENT["how_it_works"])
if not isinstance(how_items, list):
    how_items = DEFAULT_HOMEPAGE_CONTENT["how_it_works"]
how_cards_html_parts: list[str] = []
for idx, item in enumerate(how_items[:3], start=1):
    if not isinstance(item, dict):
        continue
    step = escape(str(item.get("step", f"{idx:02d}")))
    title = escape(str(item.get("title", f"Step {idx}")))
    description = escape(str(item.get("description", "")))
    how_cards_html_parts.append(
        f"""
        <div class="orbit-card">
          <div class="orbit-step">{step}</div>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
        """
    )
how_cards_html = "".join(how_cards_html_parts)

features = homepage_content.get("features", DEFAULT_HOMEPAGE_CONTENT["features"])
if not isinstance(features, list):
    features = DEFAULT_HOMEPAGE_CONTENT["features"]
feature_blocks: list[str] = []
for idx, item in enumerate(features):
    if not isinstance(item, dict):
        continue
    alt_class = " alt" if idx % 2 == 1 else ""
    label = escape(str(item.get("label", "Feature")))
    headline = escape(str(item.get("headline", "Feature Title")))
    body = escape(str(item.get("body", "")))
    visual_title = escape(str(item.get("visual_title", "Details")))
    visual_body = escape(str(item.get("visual_body", "")))
    feature_blocks.append(
        f"""
        <div class="orbit-feature{alt_class}">
          <div class="orbit-text">
            <div class="orbit-label">{label}</div>
            <h2>{headline}</h2>
            <p>{body}</p>
          </div>
          <div class="orbit-visual">
            <h4>{visual_title}</h4>
            <p>{visual_body}</p>
          </div>
        </div>
        """
    )
features_html = "".join(feature_blocks)

chat_config = homepage_content.get("chat_preview", DEFAULT_HOMEPAGE_CONTENT["chat_preview"])
chat_messages = chat_config.get("messages", DEFAULT_HOMEPAGE_CONTENT["chat_preview"]["messages"])
if not isinstance(chat_messages, list):
    chat_messages = DEFAULT_HOMEPAGE_CONTENT["chat_preview"]["messages"]
chat_rows: list[str] = []
for message in chat_messages[:8]:
    if not isinstance(message, dict):
        continue
    role = str(message.get("role", "user")).lower()
    text = escape(str(message.get("text", "")))
    if role == "assistant":
        chat_rows.append(
            f"""
            <div class="orbit-chat-row assistant">
              <div class="orbit-assistant-wrap">
                <span class="orbit-ai-icon"></span>
                <div class="orbit-bubble assistant">{text}</div>
              </div>
            </div>
            """
        )
    else:
        chat_rows.append(
            f"""
            <div class="orbit-chat-row user">
              <div class="orbit-bubble user">{text}</div>
            </div>
            """
        )
chat_html = "".join(chat_rows)

st.markdown(
    """
<style>
[data-testid="stAppViewContainer"] .main .block-container {
  max-width: 100%;
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 0;
  padding-right: 0;
}
.orbit-root {
  background: #0A0A0F;
  color: #FFFFFF;
}
.orbit-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px;
}
.orbit-section {
  padding: 80px 0;
}
.orbit-hero {
  padding: 120px 0 32px 0;
  text-align: center;
}
.orbit-hero h1 {
  font-size: 56px;
  line-height: 1.2;
  color: #FFFFFF;
  margin: 0;
}
.orbit-hero p {
  margin: 20px auto 0 auto;
  max-width: 860px;
  font-size: 18px;
  line-height: 1.6;
  color: #9999AA;
}
.orbit-cta-wrap {
  background: #0A0A0F;
  padding: 0 0 88px 0;
}
.orbit-cta-wrap .stButton > button {
  background: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #FFFFFF !important;
  border-radius: 999px !important;
  padding: 14px 32px !important;
  font-size: 16px !important;
  line-height: 1.2 !important;
}
.orbit-cta-wrap .stButton > button:hover {
  opacity: 0.92;
}
.orbit-how {
  background: #111118;
}
.orbit-how-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
}
.orbit-card {
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 40px;
  background: transparent;
}
.orbit-step {
  font-size: 48px;
  line-height: 1;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.06);
  margin-bottom: 24px;
}
.orbit-card h3 {
  font-size: 24px;
  line-height: 1.2;
  color: #FFFFFF;
  margin: 0 0 12px 0;
}
.orbit-card p {
  margin: 0;
  color: #9999AA;
  font-size: 16px;
  line-height: 1.6;
}
.orbit-features .orbit-feature {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
  margin-bottom: 80px;
}
.orbit-features .orbit-feature:last-child {
  margin-bottom: 0;
}
.orbit-feature.alt .orbit-text {
  order: 2;
}
.orbit-feature.alt .orbit-visual {
  order: 1;
}
.orbit-label {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #8B5CF6;
  font-size: 12px;
  margin-bottom: 14px;
}
.orbit-text h2 {
  margin: 0 0 16px 0;
  color: #FFFFFF;
  font-size: 32px;
  line-height: 1.2;
}
.orbit-text p {
  margin: 0;
  color: #9999AA;
  font-size: 17px;
  line-height: 1.6;
}
.orbit-visual {
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  background: #111118;
  padding: 28px;
}
.orbit-visual h4 {
  margin: 0 0 12px 0;
  color: #FFFFFF;
  font-size: 20px;
  line-height: 1.2;
}
.orbit-visual p {
  margin: 0;
  color: #9999AA;
  font-size: 16px;
  line-height: 1.6;
}
.orbit-chat-wrap {
  padding-top: 0;
}
.orbit-chat-card {
  max-width: 600px;
  margin: 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  background: #111118;
  padding: 26px;
}
.orbit-chat-row {
  display: flex;
  margin-bottom: 18px;
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
.orbit-bubble {
  max-width: 82%;
  border-radius: 14px;
  padding: 14px 16px;
  font-size: 16px;
  line-height: 1.6;
}
.orbit-bubble.user {
  background: #0D0E14;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #FFFFFF;
}
.orbit-bubble.assistant {
  background: #181726;
  border: 1px solid rgba(139, 92, 246, 0.25);
  color: #D7D2F8;
}
.orbit-ai-icon {
  display: inline-flex;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #8B5CF6;
  margin-right: 10px;
  flex-shrink: 0;
}
.orbit-assistant-wrap {
  display: flex;
  align-items: flex-start;
}
@media (max-width: 980px) {
  .orbit-how-grid {
    grid-template-columns: 1fr;
  }
  .orbit-features .orbit-feature {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .orbit-feature.alt .orbit-text,
  .orbit-feature.alt .orbit-visual {
    order: initial;
  }
  .orbit-hero h1 {
    font-size: 42px;
  }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="orbit-root">
  <section class="orbit-hero">
    <div class="orbit-container">
      <h1>{hero_title}</h1>
      <p>{hero_subtitle}</p>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="orbit-cta-wrap">', unsafe_allow_html=True)
left, center, right = st.columns([2.3, 2.4, 2.3])
with center:
    if st.button(hero_cta, key="hero_daily_prediction"):
        st.switch_page(daily_target)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
<div class="orbit-root">
  <section class="orbit-section orbit-how">
    <div class="orbit-container">
      <div class="orbit-how-grid">
        {how_cards_html}
      </div>
    </div>
  </section>

  <section class="orbit-section orbit-features">
    <div class="orbit-container">
      {features_html}
    </div>
  </section>

  <section class="orbit-section orbit-chat-wrap">
    <div class="orbit-container">
      <div class="orbit-chat-card">
        {chat_html}
      </div>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)
