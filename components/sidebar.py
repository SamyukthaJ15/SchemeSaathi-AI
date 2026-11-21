import streamlit as st

import config
from modules import gemini_service as G
from modules.translator import t

PAGES = [("home", "🏠", "nav_home"), ("find", "🔎", "nav_find"), ("explore", "🏛️", "nav_explore"),
         ("docs", "📄", "nav_docs"), ("scam", "🛡️", "nav_scam"), ("voice", "🎙️", "nav_voice"), ("about", "ℹ️", "nav_about")]


def render() -> str:
    with st.sidebar:
        st.markdown('<div class="brand">Scheme<span>Saathi</span> AI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="tag">{t("tagline")}</div>', unsafe_allow_html=True)
        labels = {k: f"{icon} {t(key)}" for k, icon, key in PAGES}
        st.radio("Navigation", list(labels), format_func=labels.get, key="page", label_visibility="collapsed")
        st.divider()
        # Keep selected language in session state
        st.selectbox(t("language"), list(config.LANGUAGES), format_func=lambda c: config.LANGUAGES[c][0], key="lang")
        st.toggle(t("senior_mode"), key="senior")
        st.divider()
        if config.live_ready():
            st.success(f"🟢 {t('status_live_active')}")
            st.caption(f"🤖 Gemini: {config.GEMINI_MODEL} (✅)")
            st.caption("🔍 Tavily Search: (✅)")
        else:
            st.warning(f"🟡 {t('status_demo_active')}")
            st.caption("Gemini: " + ("✅ " + config.GEMINI_MODEL if G.available() else "⚠️ Not configured"))
            st.caption("Tavily: " + ("✅ Connected" if config.TAVILY_API_KEY else "⚠️ Not configured"))
            st.info(t("demo_sidebar_note"))
    return st.session_state.page
