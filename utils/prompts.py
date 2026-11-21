"""All prompt templates. Placeholders use <<NAME>> so JSON braces are safe."""

SYSTEM = """You are SchemeSaathi AI, an assistant that helps Indian citizens understand government welfare schemes.
STRICT RULES:
1. Use ONLY facts present in the SOURCES / SCHEME DATA provided. Never invent schemes, amounts, eligibility criteria, documents, dates or URLs.
2. If a detail is not in the sources, say 'Not verified in retrieved sources' and list it under missing_information.
3. Never guarantee that a person will receive a benefit. Use cautious wording and tell the user to confirm on the official portal.
4. Prefer official government sources (gov.in, nic.in). Treat non-official sources as unverified.
5. Never ask for or repeat Aadhaar numbers, OTPs, bank details or passwords.
6. Keep language simple and respectful; many users are senior citizens or first-time internet users.
7. When communicating in an Indian language (e.g. Tamil, Hindi, Telugu, etc.), ALWAYS write in the authentic native script (e.g. தமிழ் for Tamil, हिन्दी for Hindi). NEVER use Latin/English script transliteration."""

RECOMMEND = """Analyse which government schemes may suit this citizen, using ONLY the SOURCES below.

CITIZEN PROFILE (name omitted for privacy):
<<PROFILE>>

SOURCES:
<<SOURCES>>

Return JSON exactly like:
{"schemes":[{
 "name":"official scheme name",
 "level":"Central" | "State",
 "department":"ministry / department",
 "description":"1-2 sentences",
 "why_matches":"why this profile may match, referencing profile facts",
 "eligibility":{"status":"Likely Eligible"|"Possibly Eligible"|"Not Eligible",
                "requirements":["criteria stated in the sources"],
                "matched_reasons":["profile facts that satisfy criteria"],
                "missing_information":["facts needed but unknown, or details not in sources"]},
 "benefits":["benefit stated in sources"],
 "documents":[{"name":"document","required":true,"notes":""}],
 "application_process":["step 1","step 2"],
 "official_application_url":"URL from the sources or null",
 "source_url":"MUST be one of the SOURCE URLs above, copied exactly",
 "verification_notes":"what the citizen must verify officially"}]}

Rules: return at most 8 schemes, best matches first. Only include a scheme if a source describes it. Use 'Likely Eligible' only when the stated criteria clearly match the profile; use 'Possibly Eligible' when something is unknown; use 'Not Eligible' only when a stated criterion clearly fails. Do not list documents that the sources do not mention. If nothing relevant is found return {"schemes":[]}."""

EXPLAIN = {
    "eligibility": "Explain in simple <<LANG>> (in native script) why this citizen may or may not be eligible for the scheme, criterion by criterion, and what they still need to confirm.",
    "documents": "Explain in simple <<LANG>> (in native script) each document the scheme needs, why it is needed, and where an ordinary citizen usually obtains it (only if the scheme data supports it; otherwise say it is not verified). Do not assume extra documents.",
    "procedure": "Explain in simple <<LANG>> (in native script) the step-by-step application procedure as a numbered list, with the official link, and add a reminder to confirm each step on the official portal.",
}
EXPLAIN_WRAPPER = """<<TASK>>
Write the whole answer in <<LANG>> using native script (e.g. தமிழ் for Tamil, हिन्दी for Hindi). Keep official scheme names, acronyms and URLs unchanged. Use short sentences.

SCHEME DATA (retrieved from official sources):
<<SCHEME>>

CITIZEN PROFILE:
<<PROFILE>>"""

TRANSLATE_JSON = """Translate every string VALUE in this JSON into <<LANG>> using authentic native script (for example, Tamil must be in Tamil script தமிழ், Hindi in Devanagari हिन्दी, Telugu in తెలుగు, etc. - NEVER use English transliteration).
Keep keys, structure, array lengths, numbers, URLs, official scheme names (e.g. PM-KISAN, Ayushman Bharat, NSP), and currency amounts (e.g. ₹6,000) unchanged. Return only valid JSON.

<<JSON>>"""

TRANSLATE_TEXT = "Translate into <<LANG>> using authentic native script (never English transliteration). Keep official scheme names, acronyms, numbers and URLs unchanged. Return only the translation.\n\n<<TEXT>>"

TRANSCRIBE = "Transcribe this speech exactly, in the language spoken. Output only the transcript text, nothing else. If there is no intelligible speech, output an empty string."

CHAT = """Answer the citizen's question about Indian government schemes.

CITIZEN PROFILE (may be empty):
<<PROFILE>>

SCHEMES ALREADY RECOMMENDED IN THIS SESSION:
<<SCHEMES>>

SOURCES (freshly retrieved):
<<SOURCES>>

RECENT CHAT:
<<HISTORY>>

QUESTION: <<QUESTION>>

Write the answer in <<LANG>> using authentic native script (e.g. தமிழ் for Tamil, हिन्दी for Hindi, etc.) and simple words. Ground it only in the sources and recommended schemes above. If they do not contain the answer, say it could not be verified and suggest https://www.myscheme.gov.in/. If asked whether a website is genuine, never declare it definitively safe or fraudulent; explain checks and point to official sites.
Return JSON: {"answer":"...", "sources":["URLs actually used, copied exactly"], "needs_verification":true|false, "follow_ups":["up to 3 short suggested questions in <<LANG>>"]}"""

SCAM = """Assess whether this could be a fake or misleading government-scheme message or website. You are giving risk indicators, NOT a verdict.

URL (may be empty): <<URL>>
MESSAGE (may be empty):
<<MESSAGE>>

RULE-BASED FLAGS ALREADY DETECTED:
<<FLAGS>>

RESEARCH SOURCES (web search about the domain and the real scheme):
<<SOURCES>>

Return JSON:
{"risk":"low"|"medium"|"high",
 "summary":"2-3 sentences; use wording like 'shows warning signs' or 'could not be verified'; never say 'definitely fake' or 'definitely safe'",
 "indicators":[{"indicator":"short name","explanation":"why suspicious","severity":"low"|"medium"|"high"}],
 "recommended_actions":["clear safety steps"]}
Write all text in <<LANG>> using native script. Keep URLs unchanged."""

SUMMARIZE = """Summarise this official-web page for a citizen in <<LANG>> using native script: what the scheme is, who may be eligible, benefits, and how to apply. Use only the text below; mark anything unclear as not verified. Max 120 words.

TITLE: <<TITLE>>
URL: <<URL>>
TEXT:
<<TEXT>>"""


def format_sources(docs, per_doc_chars: int = 1800, limit: int = 8) -> str:
    if not docs:
        return "(none retrieved)"
    parts = []
    for i, d in enumerate(docs[:limit], 1):
        parts.append(
            f"[S{i}] {d.title}\nURL: {d.url}\nOfficial government domain: {'yes' if d.official else 'NO (unverified source)'}\n"
            f"Retrieved: {d.retrieved_at}\nContent: {d.content[:per_doc_chars]}"
        )
    return "\n\n".join(parts)
