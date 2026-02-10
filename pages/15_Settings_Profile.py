from __future__ import annotations

from datetime import date

import streamlit as st

from app.services.auth_service import AuthService
from app.services.stripe_service import StripeService
from app.ui.components import app_header, auth_sidebar, format_time_ampm, parse_time_ampm
from app.ui.session import get_current_user, init_session, logout_user, require_auth
from app.utils.astro import sun_sign_for_date

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
init_session()
user = require_auth()
auth_sidebar(user)
auth = AuthService()
stripe = StripeService()

app_header("Settings / Profile", "Manage account, birth data, preferences, and subscription status.")
if st.session_state.get("settings_preferences_saved"):
    st.success("Preferences saved.")
    st.session_state["settings_preferences_saved"] = False

st.subheader("Subscription")
st.write(f"Current tier: **{user.subscription_tier}**")
if user.subscription_expires_at:
    st.write(f"Expires at: {user.subscription_expires_at.isoformat()}")
if user.stripe_customer_id:
    st.write(f"Stripe customer id: `{user.stripe_customer_id}`")
else:
    st.caption("Stripe customer profile not linked yet. Billing portal wiring is scaffolded for next step.")

if stripe.user_has_active_premium(user):
    st.success("Premium is active.")
else:
    st.warning("You are on Free tier.")

if not stripe.configured():
    st.info("Stripe checkout is not configured yet. Set Stripe env vars to enable upgrade flows.")
else:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Create Monthly Checkout Session"):
            result = stripe.create_checkout_session(user, plan="monthly")
            if result.ok and result.url:
                st.link_button("Open Checkout (Monthly)", result.url)
            else:
                st.error(result.message)
    with c2:
        if st.button("Create Yearly Checkout Session"):
            result = stripe.create_checkout_session(user, plan="yearly")
            if result.ok and result.url:
                st.link_button("Open Checkout (Yearly)", result.url)
            else:
                st.error(result.message)

    if st.button("Open Stripe Customer Portal"):
        result = stripe.create_customer_portal_session(user)
        if result.ok and result.url:
            st.link_button("Open Billing Portal", result.url)
        else:
            st.error(result.message)

st.divider()
st.subheader("Edit Birth Data")
dob = st.date_input("Date of birth", value=user.dob, min_value=date(1900, 1, 1), max_value=date.today())
has_birth_time = st.checkbox("I know my birth time", value=user.birth_time is not None)
if "settings_birth_time_ampm" not in st.session_state:
    st.session_state["settings_birth_time_ampm"] = format_time_ampm(user.birth_time)
if not has_birth_time:
    st.session_state["settings_birth_time_ampm"] = ""
birth_time = None
if has_birth_time:
    birth_time_raw = st.text_input(
        "Birth time (AM/PM)",
        key="settings_birth_time_ampm",
        placeholder="e.g. 09:30 AM",
    )
    st.caption("Use format `HH:MM AM/PM`.")
    birth_time = parse_time_ampm(birth_time_raw)
birth_location = st.text_input("Birth location", value=user.birth_location or "")
timezone = st.text_input("Timezone", value=user.timezone or "", placeholder="e.g. America/New_York")
lat = st.text_input("Latitude (optional)", value="" if user.lat is None else str(user.lat))
lng = st.text_input("Longitude (optional)", value="" if user.lng is None else str(user.lng))
save_birth_data = st.button("Save Birth Data", type="primary")

if save_birth_data:
    if has_birth_time and birth_time is None:
        st.error("Please enter birth time in `HH:MM AM/PM` format.")
    else:
        try:
            parsed_lat = float(lat) if lat.strip() else None
            parsed_lng = float(lng) if lng.strip() else None
        except ValueError:
            st.error("Latitude/Longitude must be numeric.")
        else:
            updated = auth.update_birth_data(
                user.id,
                dob=dob,
                birth_time=birth_time.isoformat() if birth_time else None,
                birth_location=birth_location.strip() or None,
                lat=parsed_lat,
                lng=parsed_lng,
                timezone=timezone.strip() or None,
            )
            st.success(f"Birth data updated. Sun sign now: {updated.sun_sign or sun_sign_for_date(updated.dob)}")
            st.info("Origin and yearly readings will recalculate on next open if the birth signature changed.")

st.divider()
st.subheader("Change Password")
with st.form("settings_change_password_form"):
    old_password = st.text_input("Current password", type="password")
    new_password = st.text_input("New password", type="password")
    confirm_password = st.text_input("Confirm new password", type="password")
    change_password_btn = st.form_submit_button("Change Password")

if change_password_btn:
    if not new_password or new_password != confirm_password:
        st.error("New password fields must match.")
    else:
        result = auth.change_password(user.id, old_password, new_password)
        if result.ok:
            st.success(result.message)
        else:
            st.error(result.message)

st.divider()
st.subheader("Notification and Theme Preferences")
with st.form("settings_preferences_form"):
    notify_daily = st.checkbox("Daily reading reminders", value=user.notify_daily_reading)
    daily_hour = st.slider(
        "Daily reading hour (24h)", min_value=0, max_value=23, value=user.daily_reading_hour or 8, step=1
    )
    notify_transits = st.checkbox("Transit alerts", value=user.notify_transit_alerts)
    theme = st.selectbox("Theme", options=["dark", "light"], index=0 if user.theme_preference == "dark" else 1)
    language = st.selectbox("Language", options=["en"], index=0)
    save_preferences = st.form_submit_button("Save Preferences")

if save_preferences:
    updated = auth.update_preferences(
        user.id,
        theme_preference=theme,
        language_preference=language,
        notify_daily_reading=notify_daily,
        daily_reading_hour=daily_hour,
        notify_transit_alerts=notify_transits,
    )
    st.session_state["settings_preferences_saved"] = True
    st.rerun()

st.divider()
st.subheader("Data & Privacy")
st.warning("Delete account is permanent and removes your profile, tokens, partner profiles, and readings.")
confirm_phrase = st.text_input("Type DELETE to confirm")
if st.button("Delete My Account", type="secondary"):
    if confirm_phrase != "DELETE":
        st.error("Type DELETE exactly to confirm.")
    else:
        result = auth.delete_account(user.id)
        if result.ok:
            logout_user()
            st.success("Account deleted.")
            st.rerun()
        else:
            st.error(result.message)
