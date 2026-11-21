import html

import streamlit as st

from modules import gemini_service as G, validation as V, voice_assistant as voice
from modules.translator import t

CLS = {V.EligibilityStatus.LIKELY: ("ok", "likely"), V.EligibilityStatus.POSSIBLE: ("warn", "possibly"),
       V.EligibilityStatus.NOT: ("no", "not_eligible")}


def badge(text: str, cls: str) -> str:
    return f'<span class="badge {cls}">{html.escape(text)}</span>'


def _bullets(items):
    st.markdown("\n".join(f"- {x}" for x in items) if items else "—")


def render(disp: V.GovernmentScheme, orig: V.GovernmentScheme, idx: int, lang: str, profile_ai, on_docs) -> None:
    """disp = translated copy for display; orig = English copy for AI calls. Names/URLs are identical."""
    cls, key = CLS[disp.eligibility.status]
    ss = st.session_state
    with st.container(border=True):
        badges = badge(t(key), cls) + badge(t("central") if disp.level == V.SchemeLevel.CENTRAL else t("state"), "info")
        if disp.is_demo:
            badges += badge(t("demo_badge"), "warn")
        else:
            badges += badge(t("live_badge"), "ok")
        st.markdown(f'<div class="sname">{html.escape(disp.name)}</div>{badges}'
                    f'<div class="meta">{html.escape(disp.department)}</div>', unsafe_allow_html=True)
        st.write(disp.description)
        if disp.why_matches:
            st.markdown(f"**{t('why_match')}**")
            st.write(disp.why_matches)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{t('eligibility')}**")
            _bullets(disp.eligibility.requirements)
            if disp.eligibility.missing_information:
                st.markdown(f"**{t('missing_info')}**")
                _bullets(disp.eligibility.missing_information)
        with c2:
            st.markdown(f"**{t('benefits')}**")
            _bullets(disp.benefits)
        with st.expander(f"📄 {t('documents')} ({len(disp.documents)})"):
            for d in disp.documents:
                tag = t("required") if d.required else t("optional_doc")
                st.markdown(f"- **{d.name}** ({tag})" + (f": {d.notes}" if d.notes else ""))
        with st.expander(f"📝 {t('how_apply')}"):
            for i, step in enumerate(disp.application_process, 1):
                st.markdown(f"{i}. {step}")
        l1, l2 = st.columns(2)
        if disp.official_application_url:
            l1.link_button(f"🔗 {t('apply_link')}", disp.official_application_url)
        l2.link_button(f"📚 {t('source')}", disp.source_url)
        st.markdown(f'<div class="meta">{t("retrieved")}: {html.escape(disp.last_retrieved or "—")}</div>', unsafe_allow_html=True)
        if disp.verification_notes:
            st.caption("⚠️ " + disp.verification_notes)
        b1, b2, b3, b4 = st.columns(4)
        k = f"{idx}_{orig.name}"
        if b1.button("🔊 " + t("listen"), key=f"l_{k}"):
            ss.setdefault("card_audio", {})[k] = voice.scheme_speech(disp, "all")
        if G.available():
            for col, kind, label, fn in ((b2, "elig", "explain_elig", G.explain_eligibility),
                                         (b3, "docs", "explain_docs", G.explain_documents),
                                         (b4, "proc", "explain_proc", G.explain_procedure)):
                if col.button(t(label), key=f"{kind}_{k}"):
                    with st.spinner("…"):
                        try:
                            ss.setdefault("explain", {})[(k, kind)] = fn(orig, profile_ai, lang)
                        except G.GeminiError as e:
                            st.error(str(e))
        else:
            b2.caption(t("ai_need_key"))
        if k in ss.get("card_audio", {}):
            voice.play(ss["card_audio"][k], lang)
        for kind in ("elig", "docs", "proc"):
            txt = ss.get("explain", {}).get((k, kind))
            if txt:
                st.markdown(txt)
                voice.play(txt, lang)
        st.button("✅ " + t("check_docs"), key=f"cd_{k}", on_click=on_docs, args=(idx,))


def render_compact(s: V.GovernmentScheme, idx: int) -> None:
    with st.container(border=True):
        badge_html = badge(t("demo_badge"), "warn") if s.is_demo else badge(t("live_badge"), "ok")
        st.markdown(f'<div class="sname">{html.escape(s.name)}</div>'
                    f'{badge_html}<div class="meta">{html.escape(s.department)}</div>', unsafe_allow_html=True)
        st.write(s.description)
        _bullets(s.benefits)
        st.link_button(f"🔗 {t('official_site')}", s.source_url)
