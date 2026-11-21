"""SchemeSaathi AI: Streamlit entry point.  Run:  streamlit run app.py"""
import hashlib
import html

import streamlit as st

st.set_page_config(page_title="SchemeSaathi AI", page_icon="🇮🇳", layout="wide")

import config
from components import accessibility, scheme_cards, sidebar
from modules import (demo_data, document_checker, eligibility, gemini_service as G, profile as prof,
                     scam_detector, scheme_search, translator, validation as V, voice_assistant as voice)
from modules.translator import t, t_opt, t_about
from utils.helpers import get_host, now_ist

CATEGORIES = ["All"] + list(demo_data.CATEGORY_TAGS)


def esc(x) -> str:
    return html.escape(str(x))


def init_state():
    for k, v in dict(page="home", lang="en", senior=False, profile=None, results=None, chat=[],
                     explore=None, scam=None, voice_last=None, doc_idx=0, last_audio=None,
                     tr_cache={}, explain={}, card_audio={}).items():
        st.session_state.setdefault(k, v)


def goto(page: str):
    st.session_state.page = page


def goto_docs(idx: int):
    st.session_state.doc_idx = idx
    st.session_state.page = "docs"


def profile_ai():
    p = st.session_state.profile
    return prof.to_ai_dict(p) if p else None


def current_schemes():
    r = st.session_state.results
    return r["schemes"] if r else []


# ------------------------------------------------------------------ assistant (shared by chat + voice)
def ask_assistant(question: str) -> V.ChatResponse:
    ss = st.session_state
    if not G.available():
        return V.ChatResponse(answer=t("need_key"), needs_verification=True)
    sources = []
    if config.TAVILY_API_KEY:
        try:
            sources = scheme_search.search_for_question(question, ss.profile)
        except scheme_search.SearchError:
            pass
    try:
        resp = G.chat(question, profile_ai(), current_schemes(), sources, ss.chat, ss.lang)
    except G.GeminiError as e:
        resp = V.ChatResponse(answer=str(e), needs_verification=True)
    ss.chat += [{"role": "user", "text": question}, {"role": "assistant", "text": resp.answer, "sources": resp.sources}]
    return resp


def render_answer(resp: V.ChatResponse):
    st.markdown(resp.answer)
    if resp.sources:
        st.caption("Sources: " + " · ".join(f"[{get_host(u)}]({u})" for u in resp.sources))
    if resp.needs_verification:
        st.caption("⚠️ " + t("disclaimer"))


def chat_widget():
    with st.expander("💬 " + t("ask_ai")):
        hist = st.container()
        with st.form("chat_form", clear_on_submit=True):
            q = st.text_input(t("ask_ai"), placeholder="What documents are needed for PM-KISAN?", label_visibility="collapsed")
            go = st.form_submit_button(t("send"))
        if go and q.strip():
            with st.spinner("…"):
                ask_assistant(q.strip())
        with hist:
            for m in st.session_state.chat[-8:]:
                with st.chat_message(m["role"]):
                    st.markdown(m["text"])
                    if m.get("sources"):
                        st.caption(" · ".join(f"[{get_host(u)}]({u})" for u in m["sources"]))


# ------------------------------------------------------------------ pages
def page_home():
    st.markdown(f'<div class="hero"><h1>{esc(t("welcome_title"))}</h1><p>{esc(t("welcome_sub"))}</p>'
                f'<div class="motto">{esc(t("motto"))}</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.button("🔎 " + t("cta_find"), on_click=goto, args=("find",), type="primary")
    c2.button("🎙️ " + t("nav_voice"), on_click=goto, args=("voice",))
    c3.button("🛡️ " + t("nav_scam"), on_click=goto, args=("scam",))
    st.subheader(t("feat_title"))
    feats = [("🎯", 1), ("🏛️", 2), ("📄", 3), ("🛡️", 4), ("🌐", 5), ("🎙️", 6)]
    for row in (feats[:3], feats[3:]):
        for col, (icon, n) in zip(st.columns(3), row):
            col.markdown(f'<div class="fcard"><div style="font-size:1.6rem">{icon}</div><h4>{esc(t(f"feat{n}_t"))}</h4>'
                         f'<p>{esc(t(f"feat{n}_d"))}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="senior"><b>👴 {esc(t("senior_title"))}</b><br>{esc(t("senior_text"))}</div>', unsafe_allow_html=True)
    st.subheader("🤖 " + t("ai_title"))
    st.write(t("ai_text"))
    st.button("🎙️ " + t("nav_voice"), key="home_voice", on_click=goto, args=("voice",))


def page_find():
    ss = st.session_state
    st.header("🔎 " + t("find_title"))
    st.caption(t("find_sub"))
    prof.init_form_state(ss)
    st.markdown(f"**{t('try_scenarios')}**")
    for col, (key, sc) in zip(st.columns(len(prof.SCENARIOS)), prof.SCENARIOS.items()):
        col.button(f"{sc['icon']} {t(sc['label'])}", key=f"sc_{key}", on_click=prof.apply_scenario, args=(ss, key))
    opt = t("optional")
    with st.form("profile_form"):
        a, b, c = st.columns(3)
        a.text_input(f"{t('f_name')} ({opt})", key="p_name", max_chars=80)
        b.number_input(t("f_age"), 1, 120, step=1, key="p_age")
        c.selectbox(t("f_gender"), prof.opts(V.Gender), format_func=lambda v: t_opt(v), key="p_gender")
        a, b, c = st.columns(3)
        a.selectbox(t("f_state"), config.INDIAN_STATES, key="p_state")
        b.text_input(f"{t('f_district')} ({opt})", key="p_district", max_chars=60)
        c.number_input(t("f_income"), 0, 100_000_000, step=10000, key="p_income")
        a, b, c = st.columns(3)
        a.selectbox(t("f_occupation"), prof.opts(V.Occupation), format_func=lambda v: t_opt(v), key="p_occ")
        b.selectbox(t("f_education"), prof.opts(V.Education), format_func=lambda v: t_opt(v), key="p_edu")
        c.selectbox(f"{t('f_category')} ({opt})", prof.opts(V.SocialCategory, True), format_func=lambda v: t_opt(v), key="p_cat")
        a, b, c = st.columns(3)
        a.selectbox(t("f_residence"), prof.opts(V.Residence), format_func=lambda v: t_opt(v), key="p_area")
        b.selectbox(f"{t('f_marital')} ({opt})", prof.opts(V.MaritalStatus, True), format_func=lambda v: t_opt(v), key="p_marital")
        c.selectbox(f"{t('f_disability')} ({opt})", prof.opts(V.DisabilityStatus, True), format_func=lambda v: t_opt(v), key="p_disab")
        a, _, _ = st.columns(3)
        a.number_input(f"{t('f_family')} ({opt})", 1, 30, step=1, key="p_family")
        submitted = st.form_submit_button("🔎 " + t("submit"), type="primary")
    if submitted:
        try:
            profile = prof.build_profile(ss)
        except V.ValidationError as e:
            st.error(t("correct_errors"))
            for m in V.format_errors(e):
                st.write("• " + m)
        else:
            ss.profile = profile
            ss.explain, ss.card_audio = {}, {}
            with st.spinner(t("searching")):
                ss.results = eligibility.find_schemes(profile)
    if ss.results:
        render_results(ss.results)


def render_results(res: dict):
    ss = st.session_state
    st.divider()
    st.subheader(t("results_title"))
    for m in res.get("messages", []):
        (st.warning if res["mode"] != "live" else st.info)(m)

    if res["mode"] == "demo":
        st.warning(f"🧪 **{t('demo_banner')}**")
    elif res["mode"] == "live":
        st.success(f"🟢 **{t('live_banner')}** ({t('retrieved')}: {res['ran_at']})")
        if any(d.cached for d in res.get("sources", [])):
            st.info(t("cached_note"))
        if res.get("dropped"):
            st.caption(f"{res['dropped']} AI suggestion(s) were discarded because they could not be matched to a retrieved source.")
    elif res["mode"] == "partial_tavily_only":
        st.warning(f"⚠️ **{t('partial_banner')}** ({t('retrieved')}: {res['ran_at']})")
    elif res["mode"] == "empty" or (res["mode"] == "live" and not res.get("schemes")):
        st.info(t("no_schemes_found"))

    schemes = res.get("schemes", [])
    shown = [(i, s) for i, s in enumerate(schemes) if s.eligibility.status != V.EligibilityStatus.NOT]
    hidden = [(i, s) for i, s in enumerate(schemes) if s.eligibility.status == V.EligibilityStatus.NOT]
    if schemes and ss.lang != "en":
        with st.spinner("…"):
            tr = {i: translator.translate_scheme(s, ss.lang) for i, s in enumerate(schemes)}
    else:
        tr = dict(enumerate(schemes))
    for i, s in shown:
        scheme_cards.render(tr[i], s, i, ss.lang, profile_ai(), goto_docs)
    if hidden:
        with st.expander(f"{t('not_eligible_group')} ({len(hidden)})"):
            for i, s in hidden:
                scheme_cards.render(tr[i], s, i, ss.lang, profile_ai(), goto_docs)
    if res.get("sources"):
        with st.expander(f"🔗 {t('sources_used')} ({len(res['sources'])})"):
            for d in res["sources"]:
                flag = "🏛️ " + t("official_site") if d.official else "⚠️ " + t("unverified_site")
                badge_type = "cached" if d.cached else "LIVE"
                st.markdown(f"- [{d.title}]({d.url}): {flag} · [{badge_type}] · {t('retrieved')}: {d.retrieved_at}")
    st.markdown(f'<div class="disc">{esc(t("disclaimer"))}</div>', unsafe_allow_html=True)


def page_explore():
    ss = st.session_state
    st.header("🏛️ " + t("explore_title"))
    a, b, c = st.columns(3)
    state = a.selectbox(t("f_state"), ["All India (Central)"] + config.INDIAN_STATES, format_func=lambda s: t_opt(s), key="ex_state")
    cat = b.selectbox(t("category"), CATEGORIES, format_func=lambda c: t_opt(c), key="ex_cat")
    kw = c.text_input(t("keyword"), key="ex_kw", max_chars=100)
    if st.button("🔎 " + t("search"), type="primary"):
        if config.TAVILY_API_KEY:
            try:
                with st.spinner("…"):
                    ss.explore = dict(demo=False, docs=scheme_search.explore(state, cat, kw), at=now_ist(), error=None)
            except scheme_search.SearchError as e:
                ss.explore = dict(demo=False, docs=[], at=now_ist(), error=str(e))
        else:
            ss.explore = dict(demo=True, docs=demo_data.demo_catalog(cat), at=now_ist(), error=None)
    ex = ss.explore
    if not ex:
        return
    if ex.get("error"):
        st.error(ex["error"])
    if ex.get("demo"):
        st.warning("🧪 " + t("demo_banner") + " " + t("demo_sidebar_note"))
        for i, s in enumerate(ex.get("docs", [])):
            scheme_cards.render_compact(s, i)
        if not ex.get("docs"):
            st.info(t("no_demo_category"))
        return
    else:
        st.success(f"🟢 **{t('live_banner')}** ({t('retrieved')}: {ex['at']})")

    if not ex.get("docs") and not ex.get("error"):
        st.info(t("no_schemes_found"))
    for i, d in enumerate(ex.get("docs", [])):
        with st.container(border=True):
            st.markdown(f"**[{d.title}]({d.url})**")
            st.markdown(scheme_cards.badge(t("official_site") if d.official else t("unverified_site"), "ok" if d.official else "warn")
                        + scheme_cards.badge("cached" if d.cached else t("live_badge"), "info"), unsafe_allow_html=True)
            st.caption(f"{t('retrieved')}: {d.retrieved_at}")
            st.write(d.content[:400] + ("…" if len(d.content) > 400 else ""))
            if G.available() and st.button("✨ " + t("ai_summary"), key=f"sum_{i}"):
                with st.spinner("…"):
                    try:
                        ss.setdefault("summaries", {})[d.url] = G.summarize_source(d, ss.lang)
                    except G.GeminiError as e:
                        st.error(str(e))
            if d.url in ss.get("summaries", {}):
                st.markdown(ss["summaries"][d.url])
                voice.play(ss["summaries"][d.url], ss.lang)


def page_docs():
    ss = st.session_state
    st.header("📄 " + t("docs_title"))
    st.caption(t("docs_sub"))
    schemes = current_schemes()
    if not schemes:
        st.info(t("profile_first"))
        st.button("🔎 " + t("nav_find"), on_click=goto, args=("find",))
        return
    idx = st.selectbox(t("pick_scheme"), range(len(schemes)), index=min(ss.doc_idx, len(schemes) - 1),
                       format_func=lambda i: schemes[i].name, key="doc_pick")
    s = schemes[idx]
    disp = translator.translate_scheme(s, ss.lang)
    st.warning("🔒 " + t("doc_disclaimer"))
    provided, problems = [], False
    for j, d in enumerate(s.documents):
        label = disp.documents[j].name if j < len(disp.documents) else d.name
        with st.container(border=True):
            st.markdown(f"**{label}** ({t('required') if d.required else t('optional_doc')})" + (f": {d.notes}" if d.notes else ""))
            up = st.file_uploader(t("upload"), type=document_checker.ALLOWED, key=f"up_{idx}_{j}", label_visibility="collapsed")
            if up is not None:
                res = document_checker.check_file(up.name, up.getvalue())  # in memory only; never written to disk
                if res["ok"]:
                    provided.append(d.name)
                    st.success("✅ " + " ".join(res["notes"]))
                else:
                    problems = True
                    for m in res["issues"]:
                        st.error(m)
    missing = document_checker.missing_documents([d.name for d in s.documents if d.required], provided)
    st.subheader(t("missing_docs"))
    if missing:
        for m in missing:
            st.write("• " + m)
    elif not problems:
        st.success(t("docs_ready"))


def page_scam():
    ss = st.session_state
    st.header("🛡️ " + t("scam_title"))
    st.caption(t("scam_sub"))
    url = st.text_input(t("sus_url"), max_chars=500, placeholder="example: pm-kisan-yojana.xyz")
    msg = st.text_area(t("sus_msg"), max_chars=4000, height=160)
    if st.button("🔍 " + t("analyze"), type="primary"):
        if not url.strip() and not msg.strip():
            st.warning(t("scam_empty_input"))
        else:
            with st.spinner("…"):
                ss.scam = scam_detector.analyze(url, msg, ss.lang)
    a = ss.scam
    if a:
        cls = {V.RiskLevel.HIGH: "no", V.RiskLevel.MEDIUM: "warn", V.RiskLevel.UNVERIFIED: "warn", V.RiskLevel.OFFICIAL: "ok"}[a.risk_level]
        st.markdown(scheme_cards.badge(a.risk_level.value, cls) + (scheme_cards.badge(a.domain, "info") if a.domain else ""), unsafe_allow_html=True)
        st.write(a.summary)
        if not a.ai_used:
            st.caption("AI analysis was not available; this result uses rule-based checks only.")
        st.subheader(t("risk_indicators"))
        for i in a.indicators or []:
            st.markdown(f"- **{i.indicator}** ({i.severity}): {i.explanation}")
        if not a.indicators:
            st.write(t("scam_no_warnings"))
        st.subheader(t("safety_actions"))
        for x in a.recommended_actions:
            st.markdown(f"- {x}")
        st.subheader(t("official_links"))
        for u in a.official_links:
            st.markdown(f"- [{u}]({u})")
        st.markdown("- National Cyber Crime Helpline: **1930**")
        if a.research_sources:
            with st.expander(t("sources_used")):
                for d in a.research_sources:
                    st.markdown(f"- [{d.title}]({d.url}) ({t('official_site') if d.official else t('unverified_site')}), {d.retrieved_at}")
        st.caption(t("scam_disclaimer"))


def page_voice():
    ss = st.session_state
    st.header("🎙️ " + t("voice_title"))
    st.markdown(f"### {t('voice_sub')}")
    auto = st.checkbox(t("read_aloud"), value=True, key="auto_read")
    audio = st.audio_input("🎤 " + t("tap_to_speak"), key="mic")
    typed = st.text_input(t("type_instead"), key="voice_text", max_chars=500)
    question = None
    if audio is not None:
        data = audio.getvalue()
        h = hashlib.md5(data).hexdigest()
        if ss.last_audio != h:
            ss.last_audio = h
            with st.spinner("…"):
                question = voice.transcribe(data, ss.lang)
            if not question:
                st.warning(t("voice_audio_error"))
    if st.button("➡️ " + t("send"), key="voice_send", type="primary") and typed.strip():
        question = typed.strip()
    if question:
        with st.spinner("…"):
            ss.voice_last = dict(q=question, resp=ask_assistant(question), fresh=True)
    last = ss.voice_last
    if last:
        st.markdown(f"**{t('you_said')}:** {last['q']}")
        st.markdown(f"#### {t('answer')}")
        render_answer(last["resp"])
        voice.play(last["resp"].answer, ss.lang, autoplay=bool(auto and last.pop("fresh", False)))
        for f in last["resp"].follow_ups[:3]:
            st.caption("💡 " + f)
    st.divider()
    schemes = current_schemes()
    st.subheader("📢 " + t("read_scheme"))
    if not schemes:
        st.info(t("profile_first"))
        return
    i = st.selectbox(t("pick_scheme"), range(len(schemes)), format_func=lambda i: schemes[i].name, key="voice_scheme")
    disp = translator.translate_scheme(schemes[i], ss.lang)
    for col, (sec, key) in zip(st.columns(4), (("eligibility", "eligibility"), ("benefits", "benefits"), ("documents", "documents"), ("steps", "how_apply"))):
        if col.button("🔊 " + t(key), key=f"say_{sec}"):
            ss["say"] = voice.scheme_speech(disp, sec, t(key))
    if ss.get("say"):
        voice.play(ss["say"], ss.lang)


def page_about():
    st.header("ℹ️ " + t("about_title"))
    st.markdown(t_about())
    st.caption(t("motto"))


PAGE_FUNCS = dict(home=page_home, find=page_find, explore=page_explore, docs=page_docs, scam=page_scam, voice=page_voice, about=page_about)


def main():
    init_state()
    page = sidebar.render()
    accessibility.inject(st.session_state.senior)
    translator.prefetch()
    PAGE_FUNCS[page]()
    if page not in ("voice", "about"):
        chat_widget()


main()
