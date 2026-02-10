from __future__ import annotations

import streamlit as st

from app.domain.models import User
from app.repos.supabase_repo import SupabaseRepository

SESSION_USER_ID = "current_user_id"


def init_session() -> None:
    if SESSION_USER_ID not in st.session_state:
        st.session_state[SESSION_USER_ID] = None


def login_user(user: User) -> None:
    st.session_state[SESSION_USER_ID] = user.id


def logout_user() -> None:
    st.session_state[SESSION_USER_ID] = None


def get_current_user() -> User | None:
    user_id = st.session_state.get(SESSION_USER_ID)
    if not user_id:
        return None
    repo = SupabaseRepository()
    return repo.get_user_by_id(user_id)


def require_auth() -> User:
    user = get_current_user()
    if user is None:
        st.warning("Please sign in to access this page.")
        st.stop()
    return user

