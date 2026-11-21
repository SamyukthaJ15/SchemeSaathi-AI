"""Pydantic models used for user input and for validating AI output."""
import re
from enum import Enum
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

import config

__all__ = ["ValidationError"]


class Gender(str, Enum):
    FEMALE = "Female"
    MALE = "Male"
    OTHER = "Other / Prefer not to say"


class Occupation(str, Enum):
    STUDENT = "Student"
    FARMER = "Farmer"
    AG_LABOUR = "Agricultural Labourer"
    SELF = "Self-employed / Small Business"
    PRIVATE = "Private Sector Employee"
    GOVT = "Government Employee"
    DAILY = "Daily Wage Worker"
    HOMEMAKER = "Homemaker"
    UNEMPLOYED = "Unemployed"
    RETIRED = "Retired / Pensioner"
    OTHER = "Other"


class Education(str, Enum):
    NONE = "No formal education"
    PRIMARY = "Primary (up to Class 5)"
    MIDDLE = "Middle (Class 6-8)"
    SECONDARY = "Secondary (Class 10)"
    HIGHER_SEC = "Higher Secondary (Class 12)"
    DIPLOMA = "Diploma / ITI"
    GRADUATE = "Graduate"
    POSTGRAD = "Postgraduate"
    DOCTORATE = "Doctorate"


class SocialCategory(str, Enum):
    GENERAL = "General"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"


class Residence(str, Enum):
    RURAL = "Rural"
    URBAN = "Urban"


class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    WIDOWED = "Widowed"
    SEPARATED = "Divorced / Separated"


class DisabilityStatus(str, Enum):
    YES = "Yes"
    NO = "No"


class EligibilityStatus(str, Enum):
    LIKELY = "Likely Eligible"
    POSSIBLE = "Possibly Eligible"
    NOT = "Not Eligible"


class SchemeLevel(str, Enum):
    CENTRAL = "Central"
    STATE = "State"


class RiskLevel(str, Enum):
    HIGH = "High risk indicators"
    MEDIUM = "Some warning signs"
    UNVERIFIED = "Unverified"
    OFFICIAL = "Official-looking domain"


def _clean(v):
    if v is None:
        return None
    v = re.sub(r"[<>\x00-\x1f]", "", str(v)).strip()
    return v or None


def _url(v, required: bool):
    if v in (None, "", "null", "None"):
        if required:
            raise ValueError("URL is required")
        return None
    v = str(v).strip()
    p = urlparse(v)
    if p.scheme not in ("http", "https") or not p.netloc or " " in v:
        raise ValueError("Invalid URL (must start with http:// or https://)")
    return v


class Lenient(BaseModel):
    """Treats null values from the AI as 'missing' so defaults apply."""

    @model_validator(mode="before")
    @classmethod
    def _drop_none(cls, data):
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None}
        return data


class UserProfile(BaseModel):
    name: Optional[str] = Field(None, max_length=80)
    age: int = Field(ge=1, le=120)
    gender: Gender
    state: str
    district: Optional[str] = Field(None, max_length=60)
    annual_income: int = Field(ge=0, le=1_000_000_000)
    occupation: Occupation
    education: Education
    social_category: Optional[SocialCategory] = None
    residence: Residence
    marital_status: Optional[MaritalStatus] = None
    disability: Optional[DisabilityStatus] = None
    family_size: Optional[int] = Field(None, ge=1, le=30)

    @field_validator("name", "district", mode="before")
    @classmethod
    def _c(cls, v):
        return _clean(v)

    @field_validator("state")
    @classmethod
    def _state(cls, v):
        if v not in config.INDIAN_STATES:
            raise ValueError("Select a valid State / Union Territory")
        return v


class SourceDoc(BaseModel):
    title: str
    url: str
    content: str = ""
    retrieved_at: str
    official: bool = False
    cached: bool = False
    has_full_text: bool = False

    @field_validator("url")
    @classmethod
    def _u(cls, v):
        return _url(v, True)


class DocumentRequirement(Lenient):
    name: str = Field(min_length=2, max_length=150)
    required: bool = True
    notes: str = ""


class SchemeEligibility(Lenient):
    status: EligibilityStatus = EligibilityStatus.POSSIBLE
    requirements: List[str] = Field(default_factory=list)
    matched_reasons: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)

    @field_validator("status", mode="before")
    @classmethod
    def _status(cls, v):
        s = str(v).lower()
        if "not" in s:
            return EligibilityStatus.NOT
        if "likely" in s:
            return EligibilityStatus.LIKELY
        return EligibilityStatus.POSSIBLE


class GovernmentScheme(Lenient):
    name: str = Field(min_length=2, max_length=200)
    level: SchemeLevel = SchemeLevel.CENTRAL
    department: str = "Not verified in retrieved sources"
    description: str = ""
    why_matches: str = ""
    eligibility: SchemeEligibility
    benefits: List[str] = Field(default_factory=list)
    documents: List[DocumentRequirement] = Field(default_factory=list)
    application_process: List[str] = Field(default_factory=list)
    official_application_url: Optional[str] = None
    source_url: str
    last_retrieved: str = ""
    verification_notes: str = ""
    is_demo: bool = False

    @field_validator("level", mode="before")
    @classmethod
    def _level(cls, v):
        return SchemeLevel.STATE if "state" in str(v).lower() else SchemeLevel.CENTRAL

    @field_validator("documents", mode="before")
    @classmethod
    def _docs(cls, v):
        if isinstance(v, list):
            return [{"name": x} if isinstance(x, str) else x for x in v]
        return v

    @field_validator("official_application_url", mode="before")
    @classmethod
    def _oau(cls, v):
        try:
            return _url(v, False)
        except ValueError:
            return None

    @field_validator("source_url", mode="before")
    @classmethod
    def _su(cls, v):
        return _url(v, True)


class ScamIndicator(Lenient):
    indicator: str
    explanation: str = ""
    severity: str = "medium"

    @field_validator("severity", mode="before")
    @classmethod
    def _sev(cls, v):
        v = str(v).lower()
        return v if v in ("low", "medium", "high") else "medium"


class ScamAIResult(Lenient):
    risk: str = "medium"
    summary: str = ""
    indicators: List[ScamIndicator] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)


class ScamAnalysis(BaseModel):
    risk_level: RiskLevel = RiskLevel.UNVERIFIED
    domain: Optional[str] = None
    summary: str = ""
    indicators: List[ScamIndicator] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    official_links: List[str] = Field(default_factory=list)
    research_sources: List[SourceDoc] = Field(default_factory=list)
    ai_used: bool = False
    analysed_at: str = ""


class ChatResponse(Lenient):
    answer: str
    sources: List[str] = Field(default_factory=list)
    needs_verification: bool = True
    follow_ups: List[str] = Field(default_factory=list)


def format_errors(e: ValidationError) -> List[str]:
    out = []
    for err in e.errors():
        loc = ".".join(str(x) for x in err["loc"]) or "input"
        out.append(f"{loc}: {err['msg']}")
    return out
