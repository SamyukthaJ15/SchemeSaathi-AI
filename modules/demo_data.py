"""Clearly-labelled SAMPLE data for demo mode (no API keys). Summaries of real schemes with official
portals; amounts/rules change, so every entry tells the user to verify on the official site."""
from typing import List, Optional, Tuple

from modules import validation as V

NOTE = "DEMO SAMPLE: summarised from the scheme's official portal. Rules and amounts change; verify on the official website."
D = V.DocumentRequirement

_RAW = {
 "pmkisan": dict(
  name="PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)", dept="Ministry of Agriculture & Farmers Welfare",
  desc="Income support for landholding farmer families.", tags={"agriculture"},
  benefits=["Income support of ₹6,000 per year in three instalments of ₹2,000 via Direct Benefit Transfer (DBT)."],
  reqs=["Farmer family owning cultivable land", "Some categories are excluded (for example institutional landholders and certain higher-income / income-tax-paying groups): see official guidelines", "Bank account linked with Aadhaar; eKYC as required"],
  docs=[D(name="Aadhaar card", notes="Needed for registration and eKYC"), D(name="Land ownership records"),
        D(name="Bank passbook", notes="Aadhaar-seeded account"), D(name="Mobile number", required=False, notes="For OTP-based eKYC")],
  steps=["Open pmkisan.gov.in and go to 'Farmers Corner'.", "Choose 'New Farmer Registration' and enter Aadhaar, mobile number and State.", "Enter land and bank details and submit.", "Complete eKYC (OTP on the portal or biometric at a Common Service Centre).", "Use 'Know Your Status' to track. State officials verify land records."],
  apply="https://pmkisan.gov.in/", source="https://pmkisan.gov.in/"),
 "pmjay": dict(
  name="Ayushman Bharat PM-JAY (incl. Ayushman Vay Vandana for age 70+)", dept="National Health Authority, Ministry of Health & Family Welfare",
  desc="Cashless hospital cover for eligible families and senior citizens.", tags={"health", "pension"},
  benefits=["Health cover of up to ₹5 lakh per family per year for hospitalisation at empanelled hospitals.", "Residents aged 70+ can be covered under Ayushman Vay Vandana (see official portal for details)."],
  reqs=["Family listed in the PM-JAY beneficiary database (based on deprivation / occupation criteria)", "Persons aged 70 years and above are covered under Ayushman Vay Vandana"],
  docs=[D(name="Aadhaar card"), D(name="Ration card", required=False, notes="Used for family verification in some States"), D(name="Age proof", required=False, notes="For the 70+ category")],
  steps=["Visit pmjay.gov.in and use 'Am I Eligible' with your mobile number or family details.", "Or visit an empanelled hospital's Ayushman Mitra desk / a Common Service Centre.", "Complete e-KYC to generate your Ayushman card.", "Show the card at empanelled hospitals for cashless treatment."],
  apply="https://pmjay.gov.in/", source="https://pmjay.gov.in/"),
 "ignoaps": dict(
  name="Indira Gandhi National Old Age Pension Scheme (IGNOAPS), NSAP", dept="Ministry of Rural Development (National Social Assistance Programme)",
  desc="Monthly pension for elderly persons in below-poverty-line households.", tags={"pension"},
  benefits=["Monthly old-age pension. Central assistance has been ₹200 (age 60-79) and ₹500 (age 80+) per month; many States add a top-up, so check your State's amount."],
  reqs=["Age 60 years or above", "Belongs to a Below Poverty Line (BPL) household as per State list"],
  docs=[D(name="Age proof (Aadhaar / voter ID / school certificate)"), D(name="BPL card or ration card"), D(name="Bank passbook"),
        D(name="Passport-size photograph"), D(name="Residence certificate", required=False)],
  steps=["Contact your Gram Panchayat / Block office (rural) or Municipality / Ward office (urban).", "Get and fill in the pension application (many States also have an online social-welfare portal).", "Attach documents and submit; officials verify age and BPL status.", "If sanctioned, the pension is credited to your bank account."],
  apply="https://nsap.nic.in/", source="https://nsap.nic.in/"),
 "nsp": dict(
  name="National Scholarship Portal (NSP): Central & State scholarships", dept="Ministry of Education (NSP)",
  desc="One portal for many central and State scholarships.", tags={"education"},
  benefits=["Access to pre-matric, post-matric, merit-cum-means and other scholarships. Amounts depend on the specific scholarship."],
  reqs=["Eligibility differs by scholarship: course, marks, family income limit and social category", "Enrolled in a recognised institution"],
  docs=[D(name="Aadhaar card"), D(name="Income certificate", notes="Where an income limit applies"), D(name="Caste certificate", required=False, notes="Where applicable"),
        D(name="Previous year marksheet"), D(name="Bank passbook"), D(name="Institution admission / bonafide proof"),
        D(name="Passport-size photograph"), D(name="Disability certificate", required=False, notes="Where applicable")],
  steps=["Visit scholarships.gov.in and complete One Time Registration (OTR).", "Log in and check which scholarships you qualify for.", "Fill in the application, upload documents and submit before the deadline.", "Your institute and nodal officers verify; track status on the portal."],
  apply="https://scholarships.gov.in/", source="https://scholarships.gov.in/"),
 "pmayg": dict(
  name="Pradhan Mantri Awaas Yojana – Gramin (PMAY-G)", dept="Ministry of Rural Development",
  desc="Assistance for houseless or kutcha-house rural families to build a pucca house.", tags={"housing"},
  benefits=["Financial assistance for a pucca house with basic amenities, plus convergence support (e.g., toilet, MGNREGS wages) as per current guidelines."],
  reqs=["Rural household that is houseless or lives in a kutcha / dilapidated house", "Selection is generally from the approved beneficiary list (Awaas+/SECC) verified by the Gram Sabha"],
  docs=[D(name="Aadhaar card"), D(name="Bank passbook"), D(name="Job card (MGNREGS)", required=False), D(name="Ration card / BPL proof", required=False), D(name="Passport-size photograph")],
  steps=["Check whether your name is on the PMAY-G beneficiary list on pmayg.nic.in or ask your Gram Panchayat.", "If not listed, contact the Gram Panchayat / Block Development Office about inclusion.", "If selected, submit documents and bank details; money is released in instalments linked to construction progress."],
  apply="https://pmayg.nic.in/", source="https://pmayg.nic.in/"),
 "pmayu": dict(
  name="Pradhan Mantri Awaas Yojana – Urban 2.0 (PMAY-U 2.0)", dept="Ministry of Housing and Urban Affairs",
  desc="Housing assistance for eligible urban EWS / LIG / MIG families.", tags={"housing"},
  benefits=["Housing support through beneficiary-led construction/enhancement and credit-linked subsidy components (details and amounts on the official portal)."],
  reqs=["Urban household without a pucca house in the family's name (see portal for exact rule)", "Annual household income within EWS / LIG / MIG limits (broadly up to ₹3 lakh / ₹3-6 lakh / ₹6-9 lakh): verify current limits"],
  docs=[D(name="Aadhaar card"), D(name="Income proof / certificate"), D(name="Bank passbook"), D(name="Residence proof"), D(name="Passport-size photograph")],
  steps=["Visit pmay-urban.gov.in and check the application options for your category.", "Register and fill in the application, or apply via your Urban Local Body / bank.", "Upload documents and submit; follow up with the local body."],
  apply="https://pmay-urban.gov.in/", source="https://pmay-urban.gov.in/"),
 "pmmvy": dict(
  name="Pradhan Mantri Matru Vandana Yojana (PMMVY)", dept="Ministry of Women and Child Development",
  desc="Cash incentive for pregnant and lactating women.", tags={"women", "health"},
  benefits=["Cash incentive paid in instalments after pregnancy/child milestones (amounts as per current guidelines)."],
  reqs=["Pregnant or lactating woman aged 19 or above", "Generally for the first living child (see current guidelines for additional provisions)", "Women already receiving similar paid maternity benefit (e.g., many government employees) are generally excluded"],
  docs=[D(name="Aadhaar card"), D(name="Bank / post office account passbook"), D(name="Mother-Child Protection (MCP) card"), D(name="Identity proof of husband", required=False)],
  steps=["Visit your nearest Anganwadi Centre or approved health facility.", "Fill in the registration form and submit documents.", "Instalments are credited via DBT after registration, antenatal check-up and child registration/vaccination."],
  apply="https://pmmvy.wcd.gov.in/", source="https://pmmvy.wcd.gov.in/"),
 "ssy": dict(
  name="Sukanya Samriddhi Yojana", dept="Department of Posts / Ministry of Finance",
  desc="Small-savings account for the future of a girl child.", tags={"women"},
  benefits=["Savings account for a girl child with a government-notified interest rate (revised periodically) and tax benefits as per the Income Tax Act."],
  reqs=["Account opened by a parent / legal guardian for a girl child below 10 years of age", "Generally one account per girl child"],
  docs=[D(name="Girl child's birth certificate"), D(name="Guardian's identity proof"), D(name="Address proof"), D(name="Passport-size photograph")],
  steps=["Visit a post office or authorised bank with the documents.", "Fill in the account-opening form and make the minimum initial deposit.", "Collect the passbook; make deposits as per scheme rules."],
  apply="https://www.indiapost.gov.in/", source="https://www.indiapost.gov.in/"),
 "apy": dict(
  name="Atal Pension Yojana (APY)", dept="PFRDA, Ministry of Finance",
  desc="Contributory pension scheme for unorganised-sector workers.", tags={"pension", "employment"},
  benefits=["Guaranteed minimum monthly pension of ₹1,000 to ₹5,000 from age 60, depending on contribution and joining age."],
  reqs=["Age 18-40 years", "Holds a savings bank / post-office account", "Income-tax payers are not eligible to join (rule in force since October 2022)"],
  docs=[D(name="Aadhaar card"), D(name="Bank passbook"), D(name="Mobile number", required=False)],
  steps=["Visit your bank branch / post office or use net-banking.", "Fill in the APY form and choose the pension amount.", "Contribution is auto-debited from your account."],
  apply="https://www.jansuraksha.gov.in/", source="https://www.jansuraksha.gov.in/"),
}

CATEGORY_TAGS = {"Agriculture": "agriculture", "Education & Scholarships": "education", "Health": "health",
                 "Housing": "housing", "Pension & Senior Citizens": "pension", "Women & Child": "women",
                 "Employment & Skills": "employment", "Business & MSME": "business", "Disability": "disability"}
P, L, N = V.EligibilityStatus.POSSIBLE, V.EligibilityStatus.LIKELY, V.EligibilityStatus.NOT


def _assess(key: str, p: V.UserProfile) -> Optional[Tuple[V.EligibilityStatus, str, List[str]]]:
    rural, female = p.residence == V.Residence.RURAL, p.gender == V.Gender.FEMALE
    if key == "pmkisan" and p.occupation == V.Occupation.FARMER:
        return P, "You are a farmer; PM-KISAN supports landholding farmer families.", ["Do you own cultivable land (land records)?", "Exclusion criteria must be checked on the official site"]
    if key == "pmjay":
        if p.age >= 70:
            return L, "Residents aged 70+ can be covered under Ayushman Vay Vandana.", ["Confirm current enrolment steps on the portal"]
        if p.annual_income <= 300000:
            return P, "Your family income is low; PM-JAY covers families on the beneficiary database.", ["Check 'Am I Eligible' on pmjay.gov.in"]
    if key == "ignoaps" and p.age >= 60:
        return P, "You are 60+; IGNOAPS supports elderly BPL persons.", ["BPL status in your State list", "Your State's pension top-up amount"]
    if key == "nsp" and (p.occupation == V.Occupation.STUDENT or p.age <= 25):
        return P, "As a student you may qualify for one or more scholarships on NSP.", ["Course, marks and income limit of the specific scholarship"]
    if key == "pmayg" and rural and p.annual_income <= 300000:
        return P, "You live in a rural area with a modest income.", ["Whether your family is on the PMAY-G beneficiary list", "Current housing condition"]
    if key == "pmayu" and not rural and p.annual_income <= 900000:
        return P, "You live in an urban area and your income falls in a range covered by PMAY-U categories.", ["Whether your family owns a pucca house", "Exact income category limits"]
    if key == "pmmvy" and female and 19 <= p.age <= 45 and p.marital_status in (None, V.MaritalStatus.MARRIED):
        return P, "Women expecting or nursing a child may qualify.", ["Are you pregnant/lactating (first living child)?", "Not covered by other paid maternity benefit"]
    if key == "ssy" and female and p.age >= 21:
        return P, "Parents or guardians of a girl child under 10 can open this account.", ["Do you have a daughter below 10 years?"]
    if key == "apy" and 18 <= p.age <= 40 and p.occupation not in (V.Occupation.GOVT,):
        return (L if p.annual_income <= 500000 else P), "You are in the 18-40 joining age range.", ["Not an income-tax payer", "Have a savings bank account"]
    return None


def _build(key: str, status, why: str, missing: List[str]) -> V.GovernmentScheme:
    r = _RAW[key]
    return V.GovernmentScheme(
        name=r["name"], level=V.SchemeLevel.CENTRAL, department=r["dept"], description=r["desc"], why_matches=why,
        eligibility=V.SchemeEligibility(status=status, requirements=r["reqs"], matched_reasons=[why], missing_information=missing),
        benefits=r["benefits"], documents=r["docs"], application_process=r["steps"],
        official_application_url=r["apply"], source_url=r["source"],
        last_retrieved="Not retrieved live (demo sample data)", verification_notes=NOTE, is_demo=True)


def demo_schemes(p: V.UserProfile) -> List[V.GovernmentScheme]:
    out = []
    for key in _RAW:
        a = _assess(key, p)
        if a:
            out.append(_build(key, *a))
    out.sort(key=lambda s: 0 if s.eligibility.status == L else 1)
    return out


def demo_catalog(category: str) -> List[V.GovernmentScheme]:
    tag = CATEGORY_TAGS.get(category)
    return [_build(k, P, "", []) for k, r in _RAW.items() if category in ("All", None) or tag in r["tags"]]
