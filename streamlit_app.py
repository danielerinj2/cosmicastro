from __future__ import annotations

import streamlit as st

from app.services.auth_service import AuthService
from app.ui.components import app_header, auth_sidebar
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

app_header(
    "Orbit AI",
    "Orbit AI reads your birth chart down to the degree, then talks to you like a real astrologer would. Ask it anything. Anytime.",
)

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

cta_col_1, cta_col_2 = st.columns(2)
with cta_col_1:
    st.page_link(daily_target, label="Get Your Daily Prediction", icon="✨")
with cta_col_2:
    st.page_link(chat_target, label="Meet Your Astrologer", icon="🔮")

st.markdown(
    """
You've read your horoscope. It said something about "new beginnings" and "trusting the process." Cool. So did everyone else's.

Most astrology apps give you recycled paragraphs based on your sun sign alone. That's like diagnosing someone by looking at their shoes.
Your chart has twelve houses, ten planets, and dozens of aspects that make you unlike anyone else on earth.

Orbit actually uses all of it.
"""
)

st.markdown("## How It Works")
st.markdown(
    """
**Step 1 - Tell us when and where you were born.**  
Date. Time. Location. That's all we need to generate your complete natal chart with precise planetary positions, house placements, and aspects.

**Step 2 - Get readings that are actually yours.**  
Every horoscope, every insight, every forecast is generated from your unique chart. Not your sun sign. Your entire sky.

**Step 3 - Ask anything.**  
Open a conversation with Orbit and treat it like your personal astrologer. Career decisions. Relationship confusion. That weird feeling you can't shake.
Orbit connects your question to what's happening in your chart right now.
"""
)

st.markdown("## Daily Personalized Horoscope")
st.markdown(
    """
Every morning you wake up to a reading built from your natal chart crossed with the day's real-time transits.
Mercury square your natal Mars today? You'll know before you send that risky text.

No two users get the same horoscope. Ever.
"""
)

st.markdown("## Birth Chart Analysis")
st.markdown(
    """
Your full natal chart, decoded in plain language. Sun, Moon, Rising, Mercury, Venus, Mars - all the way through Pluto.
House placements. Major aspects. Pattern recognition.

Orbit doesn't just list your placements. It tells you what they mean together.
Why your Scorpio Moon and Gemini rising make you feel like two different people.
Why you keep attracting the same type.
Where your blind spots are.

This is the reading most people pay hundreds of dollars for.
"""
)

st.markdown("## Compatibility Matching")
st.markdown(
    """
Enter someone else's birth details and Orbit runs a full synastry analysis.
It compares both charts planet by planet and shows you where the chemistry lives, where the friction builds, and what the long game actually looks like.

Works for romantic partners, friends, business relationships, even that coworker you can't figure out.

No sugarcoating. Just the real dynamic between two charts.
"""
)

st.markdown("## The Chatbot Astrologer")
st.markdown(
    """
Orbit isn't a static report. It's a conversation. Ask it real questions and get real answers rooted in your chart and current transits.

**You:** I got offered a new job but something feels off. Should I take it?  
**Orbit:** Your 10th house ruler is currently being squared by transiting Saturn, which often creates doubt around career moves; but it's productive doubt.
Saturn wants you to negotiate harder, not walk away.

**You:** Not really. It's pretty rigid.  
**Orbit:** That's likely where the hesitation lives. With your chart, structure is fine but monotony kills your momentum.
I'd counter-offer with flexible terms or keep looking.
"""
)

st.markdown("## Yearly Forecast")
st.markdown(
    """
A month-by-month breakdown of your year ahead.
Major transits hitting your chart, eclipse seasons that activate your houses, Saturn and Jupiter shifts that reshape your trajectory.

Know when to push. Know when to pause. Know when the chaos has a purpose.
Updated in real time as planetary positions evolve.
"""
)

st.markdown("## What People Are Saying")
st.info("We just launched. You're early. But your readings are still accurate.")

st.markdown("## Closing")
st.markdown("Your chart already has the answers. You just haven't had the right conversation yet.")
