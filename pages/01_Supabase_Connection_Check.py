from __future__ import annotations

import streamlit as st

from app.config import AppConfig, DEFAULT_REQUIRED_TABLE_COLUMNS
from app.infra.supabase_client import get_supabase_client
from app.infra.supabase_probe import probe_connection, probe_required_columns, probe_tables

st.set_page_config(page_title="Supabase Connection Check", page_icon="🧪", layout="wide")

st.title("Supabase Connection Check")
st.caption("Pre-approval database integration verification")

config = AppConfig.from_env()
missing = config.missing_required_env()

if missing:
    st.error(f"Missing env vars: {', '.join(missing)}")
    st.info("Copy `.env.example` to `.env` and set your real Supabase values, then reload.")
    st.stop()

st.success("Environment variables detected.")
st.code(
    f"SUPABASE_URL={config.supabase_url}\n"
    f"SUPABASE_REQUIRED_TABLES={','.join(config.required_tables)}",
    language="bash",
)

run_checks = st.button("Run Live Supabase Checks", type="primary")

if run_checks:
    try:
        client = get_supabase_client()
    except Exception as exc:  # pragma: no cover - runtime configuration path
        st.error(f"Failed to initialize Supabase client: {exc}")
        st.stop()

    connection_result = probe_connection(client)
    if connection_result.ok:
        st.success(f"Connection: {connection_result.message}")
    else:
        st.error(f"Connection failed: {connection_result.message}")
        st.stop()

    st.subheader("Table Reachability")
    table_results = probe_tables(client, config.required_tables)
    for result in table_results:
        if result.ok:
            st.success(f"{result.target}: {result.message}")
        else:
            st.error(f"{result.target}: {result.message}")

    st.subheader("Required Column Checks")
    filtered_column_checks = {
        table_name: columns
        for table_name, columns in DEFAULT_REQUIRED_TABLE_COLUMNS.items()
        if table_name in config.required_tables
    }
    column_results = probe_required_columns(client, filtered_column_checks)
    for result in column_results:
        if result.ok:
            st.success(f"{result.target}: {result.message}")
        else:
            st.error(f"{result.target}: {result.message}")

    failures = [item for item in table_results + column_results if not item.ok]
    if failures:
        st.warning("One or more checks failed. Fix table names/columns/RLS and rerun.")
    else:
        st.success("All Supabase checks passed for configured tables and required columns.")

