from __future__ import annotations

import streamlit as st

from app.content.homepage_content import DEFAULT_HOMEPAGE_CONTENT, load_homepage_content, save_homepage_content
from app.ui.components import app_header, auth_sidebar
from app.ui.session import init_session, require_auth

st.set_page_config(page_title="Homepage CMS", page_icon="🛠️", layout="wide")
init_session()
user = require_auth()
auth_sidebar(user)
app_header("Homepage CMS", "Edit landing-page copy with form fields and publish instantly.")

content = load_homepage_content()

st.info("This updates the landing page content used by `streamlit_app.py`.")
st.page_link("streamlit_app.py", label="Open Homepage Preview", icon="🏠")

hero = content["hero"]
intro = content["intro"]
how = content["how_it_works"]
daily = content["daily_feature"]
birth = content["birth_chart_feature"]
compat = content["compatibility_feature"]
chatbot = content["chatbot_feature"]
yearly = content["yearly_feature"]
social = content["social_proof"]
closing = content["closing"]
cards = how["cards"]
messages = chatbot["messages"]

with st.form("homepage_cms_form"):
    st.subheader("Hero")
    hero_title = st.text_input("Hero title", value=hero["title"])
    hero_subtitle = st.text_area("Hero subtitle", value=hero["subtitle"], height=80)
    hero_cta_text = st.text_input("Hero CTA text", value=hero["cta_text"])

    st.divider()
    st.subheader("Intro")
    intro_p1 = st.text_area("Intro paragraph 1", value=intro["paragraph_1"], height=90)
    intro_p2 = st.text_area("Intro paragraph 2", value=intro["paragraph_2"], height=90)
    intro_punch = st.text_input("Intro punch line", value=intro["punch_line"])

    st.divider()
    st.subheader("How It Works")
    how_label = st.text_input("Section label", value=how["label"])

    how_cols = st.columns(3)
    with how_cols[0]:
        step1 = st.text_input("Card 1 step", value=cards[0]["step"])
        title1 = st.text_input("Card 1 title", value=cards[0]["title"])
        body1 = st.text_area("Card 1 body", value=cards[0]["body"], height=140)
    with how_cols[1]:
        step2 = st.text_input("Card 2 step", value=cards[1]["step"])
        title2 = st.text_input("Card 2 title", value=cards[1]["title"])
        body2 = st.text_area("Card 2 body", value=cards[1]["body"], height=140)
    with how_cols[2]:
        step3 = st.text_input("Card 3 step", value=cards[2]["step"])
        title3 = st.text_input("Card 3 title", value=cards[2]["title"])
        body3 = st.text_area("Card 3 body", value=cards[2]["body"], height=140)

    st.divider()
    st.subheader("Daily Feature")
    daily_label = st.text_input("Daily label", value=daily["label"])
    daily_title = st.text_input("Daily title", value=daily["title"])
    daily_p1 = st.text_area("Daily paragraph", value=daily["paragraph_1"], height=90)
    daily_tag = st.text_input("Daily tagline", value=daily["tagline"])

    st.divider()
    st.subheader("Birth Chart Feature")
    birth_label = st.text_input("Birth chart label", value=birth["label"])
    birth_title = st.text_input("Birth chart title", value=birth["title"])
    birth_p1 = st.text_area("Birth chart paragraph 1", value=birth["paragraph_1"], height=90)
    birth_p2 = st.text_area("Birth chart paragraph 2", value=birth["paragraph_2"], height=90)
    birth_tag = st.text_input("Birth chart tagline", value=birth["tagline"])

    st.divider()
    st.subheader("Compatibility Feature")
    compat_label = st.text_input("Compatibility label", value=compat["label"])
    compat_title = st.text_input("Compatibility title", value=compat["title"])
    compat_p1 = st.text_area("Compatibility paragraph 1", value=compat["paragraph_1"], height=90)
    compat_p2 = st.text_area("Compatibility paragraph 2", value=compat["paragraph_2"], height=90)
    compat_tag = st.text_input("Compatibility tagline", value=compat["tagline"])

    st.divider()
    st.subheader("Chatbot Feature")
    chatbot_label = st.text_input("Chatbot label", value=chatbot["label"])
    chatbot_title = st.text_input("Chatbot title", value=chatbot["title"])
    chatbot_intro = st.text_area("Chatbot intro", value=chatbot["intro"], height=90)

    chat_cols = st.columns(2)
    with chat_cols[0]:
        user_msg_1 = st.text_area("User message 1", value=messages[0]["text"], height=90)
        user_msg_2 = st.text_area("User message 2", value=messages[2]["text"], height=90)
    with chat_cols[1]:
        orbit_msg_1 = st.text_area("Orbit message 1", value=messages[1]["text"], height=90)
        orbit_msg_2 = st.text_area("Orbit message 2", value=messages[3]["text"], height=90)

    chatbot_closing = st.text_area("Chatbot closing line", value=chatbot["closing_line"], height=90)

    st.divider()
    st.subheader("Yearly Feature")
    yearly_label = st.text_input("Yearly label", value=yearly["label"])
    yearly_title = st.text_input("Yearly title", value=yearly["title"])
    yearly_p1 = st.text_area("Yearly paragraph 1", value=yearly["paragraph_1"], height=90)
    yearly_p2 = st.text_area("Yearly paragraph 2", value=yearly["paragraph_2"], height=90)
    yearly_tag = st.text_input("Yearly tagline", value=yearly["tagline"])

    st.divider()
    st.subheader("Social Proof")
    social_title = st.text_input("Social title", value=social["title"])
    social_line = st.text_input("Social line", value=social["line"])
    social_placeholder = st.text_input("Testimonials placeholder", value=social["placeholder_text"])

    st.divider()
    st.subheader("Closing")
    closing_title = st.text_input("Closing title", value=closing["title"])
    closing_subtitle = st.text_input("Closing subtitle", value=closing["subtitle"])
    closing_cta = st.text_input("Closing CTA text", value=closing["cta_text"])

    save_col, reset_col = st.columns(2)
    with save_col:
        save_clicked = st.form_submit_button("Save Homepage Changes", type="primary")
    with reset_col:
        reset_clicked = st.form_submit_button("Reset To Defaults")

if reset_clicked:
    save_homepage_content(DEFAULT_HOMEPAGE_CONTENT)
    st.success("Reset complete. Default homepage content restored.")
    st.rerun()

if save_clicked:
    updated = {
        "hero": {
            "title": hero_title,
            "subtitle": hero_subtitle,
            "cta_text": hero_cta_text,
        },
        "intro": {
            "paragraph_1": intro_p1,
            "paragraph_2": intro_p2,
            "punch_line": intro_punch,
        },
        "how_it_works": {
            "label": how_label,
            "cards": [
                {"step": step1, "title": title1, "body": body1},
                {"step": step2, "title": title2, "body": body2},
                {"step": step3, "title": title3, "body": body3},
            ],
        },
        "daily_feature": {
            "label": daily_label,
            "title": daily_title,
            "paragraph_1": daily_p1,
            "tagline": daily_tag,
        },
        "birth_chart_feature": {
            "label": birth_label,
            "title": birth_title,
            "paragraph_1": birth_p1,
            "paragraph_2": birth_p2,
            "tagline": birth_tag,
        },
        "compatibility_feature": {
            "label": compat_label,
            "title": compat_title,
            "paragraph_1": compat_p1,
            "paragraph_2": compat_p2,
            "tagline": compat_tag,
        },
        "chatbot_feature": {
            "label": chatbot_label,
            "title": chatbot_title,
            "intro": chatbot_intro,
            "messages": [
                {"role": "user", "text": user_msg_1},
                {"role": "assistant", "text": orbit_msg_1},
                {"role": "user", "text": user_msg_2},
                {"role": "assistant", "text": orbit_msg_2},
            ],
            "closing_line": chatbot_closing,
        },
        "yearly_feature": {
            "label": yearly_label,
            "title": yearly_title,
            "paragraph_1": yearly_p1,
            "paragraph_2": yearly_p2,
            "tagline": yearly_tag,
        },
        "social_proof": {
            "title": social_title,
            "line": social_line,
            "placeholder_text": social_placeholder,
        },
        "closing": {
            "title": closing_title,
            "subtitle": closing_subtitle,
            "cta_text": closing_cta,
        },
    }
    save_homepage_content(updated)
    st.success("Homepage content updated and published.")
    st.rerun()
