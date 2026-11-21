"""Profile form state, sample scenarios and conversion to validated/AI-safe dicts."""
from enum import Enum
from typing import Optional

import config
from modules import validation as V

SCENARIOS = {
    "student": dict(icon="🎓", label="sc_student", p_age=20, p_gender="Female", p_state="Tamil Nadu",
                    p_income=250000, p_occ="Student", p_edu="Higher Secondary (Class 12)", p_cat="OBC",
                    p_area="Urban", p_marital="Single", p_disab="No", p_family=4),
    "farmer": dict(icon="🌾", label="sc_farmer", p_age=45, p_gender="Male", p_state="Uttar Pradesh",
                   p_income=120000, p_occ="Farmer", p_edu="Secondary (Class 10)", p_cat="General",
                   p_area="Rural", p_marital="Married", p_disab="No", p_family=5),
    "senior": dict(icon="👵", label="sc_senior", p_age=65, p_gender="Male", p_state="Tamil Nadu",
                   p_income=90000, p_occ="Retired / Pensioner", p_edu="Primary (up to Class 5)", p_cat="General",
                   p_area="Rural", p_marital="Married", p_disab="No", p_family=2),
    "woman": dict(icon="👩", label="sc_woman", p_age=29, p_gender="Female", p_state="Maharashtra",
                  p_income=180000, p_occ="Homemaker", p_edu="Higher Secondary (Class 12)", p_cat="SC",
                  p_area="Rural", p_marital="Married", p_disab="No", p_family=4),
    "family": dict(icon="🏠", label="sc_family", p_age=38, p_gender="Male", p_state="Bihar",
                   p_income=110000, p_occ="Daily Wage Worker", p_edu="Middle (Class 6-8)", p_cat="SC",
                   p_area="Rural", p_marital="Married", p_disab="No", p_family=6),
}

DEFAULTS = dict(p_name="", p_age=30, p_gender="Female", p_state="Tamil Nadu", p_district="", p_income=200000,
                p_occ="Student", p_edu="Graduate", p_cat="Prefer not to say", p_area="Urban",
                p_marital="Prefer not to say", p_disab="Prefer not to say", p_family=4)


def opts(enum_cls, optional: bool = False):
    vals = [e.value for e in enum_cls]
    return vals + ["Prefer not to say"] if optional else vals


def init_form_state(ss):
    for k, v in DEFAULTS.items():
        ss.setdefault(k, v)


def apply_scenario(ss, key: str):
    for k, v in SCENARIOS[key].items():
        if k.startswith("p_"):
            ss[k] = v
    ss["p_name"] = ""
    ss["p_district"] = ""


def _opt(v) -> Optional[str]:
    return None if v in (None, "", "Prefer not to say") else v


def build_profile(ss) -> V.UserProfile:
    """Raises pydantic ValidationError on bad input."""
    return V.UserProfile.model_validate(dict(
        name=ss.get("p_name"), age=ss.get("p_age"), gender=ss.get("p_gender"), state=ss.get("p_state"),
        district=ss.get("p_district"), annual_income=ss.get("p_income"), occupation=ss.get("p_occ"),
        education=ss.get("p_edu"), social_category=_opt(ss.get("p_cat")), residence=ss.get("p_area"),
        marital_status=_opt(ss.get("p_marital")), disability=_opt(ss.get("p_disab")),
        family_size=ss.get("p_family"),
    ))


def to_ai_dict(p: V.UserProfile) -> dict:
    """Profile sent to AI/search. The person's name is deliberately excluded."""
    d = p.model_dump(mode="json", exclude={"name"})
    return {k: v for k, v in d.items() if v not in (None, "")}
