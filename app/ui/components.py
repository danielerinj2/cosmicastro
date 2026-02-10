from __future__ import annotations

import os

import streamlit as st

from app.constants import LAUNCH_TRUST_MESSAGE
from app.domain.models import User
from app.services.stripe_service import StripeService
from app.ui.session import logout_user


def app_header(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def auth_sidebar(user: User | None) -> None:
    with st.sidebar:
        st.markdown("## Discover Your Cosmic Self")
        if user:
            st.write(f"Signed in as **{user.first_name}**")
            st.write(f"Plan: `{user.subscription_tier}`")
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
