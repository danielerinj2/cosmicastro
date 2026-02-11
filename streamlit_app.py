from __future__ import annotations

import streamlit as st

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
<div class="orbit-root">
  <section class="orbit-hero">
    <div class="orbit-container">
      <h1>Your birth chart. Your personal astrologer.</h1>
      <p>Orbit reads your complete natal chart and gives you real, personalized guidance - not generic horoscope fluff.</p>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="orbit-cta-wrap">', unsafe_allow_html=True)
left, center, right = st.columns([2.3, 2.4, 2.3])
with center:
    if st.button("Get Your Daily Prediction", key="hero_daily_prediction"):
        st.switch_page(daily_target)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="orbit-root">
  <section class="orbit-section orbit-how">
    <div class="orbit-container">
      <div class="orbit-how-grid">
        <div class="orbit-card">
          <div class="orbit-step">01</div>
          <h3>Enter Your Birth Details</h3>
          <p>Date, time, and location are enough to build your precise chart.</p>
        </div>
        <div class="orbit-card">
          <div class="orbit-step">02</div>
          <h3>Get Your Full Chart</h3>
          <p>Planets, houses, and aspects are mapped together in one coherent reading.</p>
        </div>
        <div class="orbit-card">
          <div class="orbit-step">03</div>
          <h3>Ask Anything</h3>
          <p>Chat with your personal AI astrologer for direct guidance on real decisions.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="orbit-section orbit-features">
    <div class="orbit-container">
      <div class="orbit-feature">
        <div class="orbit-text">
          <div class="orbit-label">Daily</div>
          <h2>Daily Personalized Horoscope</h2>
          <p>Each reading is built from your natal chart and live transits so you get concrete, relevant guidance every day.</p>
        </div>
        <div class="orbit-visual">
          <h4>Transit-Aware Daily Insight</h4>
          <p>Designed for fast clarity: one grounded theme, relationship signal, career focus, and wellness recommendation.</p>
        </div>
      </div>

      <div class="orbit-feature alt">
        <div class="orbit-text">
          <div class="orbit-label">Natal</div>
          <h2>Birth Chart Analysis</h2>
          <p>Orbit combines signs, houses, and aspects into one readable narrative so you can understand your core patterns and blind spots.</p>
        </div>
        <div class="orbit-visual">
          <h4>Whole-Chart Interpretation</h4>
          <p>No isolated placement blurbs. Your chart is interpreted as one system with meaningful connections.</p>
        </div>
      </div>

      <div class="orbit-feature">
        <div class="orbit-text">
          <div class="orbit-label">Synastry</div>
          <h2>Compatibility Matching</h2>
          <p>Compare two charts across emotional flow, communication style, chemistry, long-term stability, and growth dynamics.</p>
        </div>
        <div class="orbit-visual">
          <h4>Real Dynamic, Not A Score</h4>
          <p>Get a dimensional read on where the connection is smooth, where it is tense, and what to do about it.</p>
        </div>
      </div>

      <div class="orbit-feature alt">
        <div class="orbit-text">
          <div class="orbit-label">Conversation</div>
          <h2>The Chatbot Astrologer</h2>
          <p>Ask direct questions and get chart-grounded responses instantly. Orbit remembers your context and answers with practical detail.</p>
        </div>
        <div class="orbit-visual">
          <h4>Context-Aware Guidance</h4>
          <p>Career move, relationship tension, timing confusion - ask one question and get an actionable next step.</p>
        </div>
      </div>

      <div class="orbit-feature">
        <div class="orbit-text">
          <div class="orbit-label">Long-Range</div>
          <h2>Yearly Forecast</h2>
          <p>See the year as a timeline of themes so you know when to push, when to pause, and where your focus will matter most.</p>
        </div>
        <div class="orbit-visual">
          <h4>Month-by-Month Focus</h4>
          <p>Track major activation periods and use them intentionally instead of reacting late.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="orbit-section orbit-chat-wrap">
    <div class="orbit-container">
      <div class="orbit-chat-card">
        <div class="orbit-chat-row user">
          <div class="orbit-bubble user">I got offered a new job but something feels off. Should I take it?</div>
        </div>
        <div class="orbit-chat-row assistant">
          <div class="orbit-assistant-wrap">
            <span class="orbit-ai-icon"></span>
            <div class="orbit-bubble assistant">Your 10th house ruler is being squared by transiting Saturn, which can create productive doubt around career moves. Saturn is asking for better terms, not automatic rejection.</div>
          </div>
        </div>
        <div class="orbit-chat-row user">
          <div class="orbit-bubble user">It seems rigid and I am worried I will lose momentum.</div>
        </div>
        <div class="orbit-chat-row assistant">
          <div class="orbit-assistant-wrap">
            <span class="orbit-ai-icon"></span>
            <div class="orbit-bubble assistant">That tracks your chart pattern. Structure helps you, but monotony drains you. Counter-offer for flexibility first. If they cannot move, keep looking while this transit tightens your standards.</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</div>
""",
    unsafe_allow_html=True,
)
