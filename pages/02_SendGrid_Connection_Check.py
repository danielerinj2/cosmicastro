from __future__ import annotations

import streamlit as st

from app.config import AppConfig
from app.infra.sendgrid_probe import probe_sendgrid_key

st.set_page_config(page_title="SendGrid Connection Check", page_icon="📨", layout="wide")

st.title("SendGrid Connection Check")
st.caption("Validate API key and permissions without sending email")

config = AppConfig.from_env()
missing = config.missing_sendgrid_env()

if missing:
    st.error(f"Missing env vars: {', '.join(missing)}")
    st.info("Set SendGrid values in `.env` and reload.")
    st.stop()

st.success("SendGrid environment variables detected.")
st.code(
    f"EMAIL_PROVIDER={config.email_provider}\n"
    f"SENDGRID_FROM_EMAIL={config.sendgrid_from_email}\n"
    f"SENDGRID_REGION={config.sendgrid_region}",
    language="bash",
)

if st.button("Run Live SendGrid Check", type="primary"):
    result = probe_sendgrid_key(
        api_key=config.sendgrid_api_key,
        region=config.sendgrid_region,
    )

    if not result.ok:
        st.error(result.message)
        st.stop()

    st.success(result.message)

    has_mail_send = "mail.send" in result.scopes
    if has_mail_send:
        st.success("`mail.send` scope is present.")
    else:
        st.error("`mail.send` scope is missing. Update API key permissions.")

    st.subheader("API Key Scopes")
    for scope in result.scopes:
        st.write(f"- {scope}")

