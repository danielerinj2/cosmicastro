from __future__ import annotations

import requests
import streamlit as st

from app.config import AppConfig
from app.ui.components import auth_sidebar
from app.ui.session import get_current_user, init_session

st.set_page_config(page_title="Stripe Connection Check", page_icon="💳", layout="wide")
init_session()
auth_sidebar(get_current_user())

st.title("Stripe Connection Check")
st.caption("Validate Stripe key and configured price ids.")

config = AppConfig.from_env()
missing = config.missing_stripe_env()
if missing:
    st.error(f"Missing env vars: {', '.join(missing)}")
    st.stop()

st.success("Stripe env vars detected.")
st.code(
    f"APP_BASE_URL={config.app_base_url}\n"
    f"STRIPE_PRICE_MONTHLY={config.stripe_price_monthly}\n"
    f"STRIPE_PRICE_YEARLY={config.stripe_price_yearly}",
    language="bash",
)

if st.button("Run Live Stripe Check", type="primary"):
    headers = {"Authorization": f"Bearer {config.stripe_secret_key}"}
    try:
        response = requests.get("https://api.stripe.com/v1/prices?limit=1", headers=headers, timeout=20)
    except Exception as exc:  # pragma: no cover
        st.error(str(exc))
        st.stop()

    if response.status_code != 200:
        st.error(f"Stripe HTTP {response.status_code}: {response.text[:300]}")
    else:
        st.success("Stripe API key is valid.")
