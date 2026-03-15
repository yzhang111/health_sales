from __future__ import annotations

from typing import Any

from app.models import AssessmentStatus, Confidence, Priority, now_iso


RED_FLAG_KEYWORDS = {
    "acute",
    "severe",
    "worsening",
    "chest pain",
    "bleeding",
    "fainting",
    "high fever",
}


def contains_red_flag_text(texts: list[str]) -> bool:
    haystack = " ".join(texts).lower()
    return any(keyword in haystack for keyword in RED_FLAG_KEYWORDS)


def detect_red_flags(customer: dict[str, Any], intake: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    complaints = intake.get("complaints", [])
    special_events = intake.get("special_events", [])
    med_conflict_items = intake.get("meds_and_contraindications", [])
    meds = customer.get("medications", [])
    contraindications = customer.get("allergies_or_contraindications", [])

    if customer.get("recent_surgery"):
        reasons.append("Recent surgery present; requires physician-first validation.")

    if contains_red_flag_text(complaints + special_events):
        reasons.append("Acute or worsening symptom keywords detected.")

    med_conflict_words = " ".join((meds + contraindications + med_conflict_items)).lower()
    if any(token in med_conflict_words for token in ["anticoagulant", "warfarin", "contraindication", "allergy"]):
        reasons.append("Potential medication/contraindication conflict detected.")

    is_red = bool(reasons)
    return is_red, reasons


def score_nutrition_directions(customer: dict[str, Any], intake: dict[str, Any]) -> list[dict[str, Any]]:
    complaints = " ".join(intake.get("complaints", [])).lower()
    lifestyle = " ".join(intake.get("lifestyle_answers", {}).values()).lower()
    goals = " ".join(intake.get("goals", [])).lower()

    scored: list[dict[str, Any]] = []

    if any(term in (complaints + lifestyle + goals) for term in ["sleep", "insomnia", "wake up", "stress"]):
        scored.append(
            {
                "direction": "Sleep support",
                "priority": Priority.high.value,
                "confidence": Confidence.medium.value,
                "trigger_reasons": ["Sleep/stress related signals in complaint and lifestyle answers."],
                "risk_notes": ["Non-diagnostic guidance only.", "Escalate if symptoms worsen."],
            }
        )

    if customer.get("recent_surgery") or "recovery" in complaints:
        scored.append(
            {
                "direction": "Post-surgery nutrition support (general)",
                "priority": Priority.high.value,
                "confidence": Confidence.low.value,
                "trigger_reasons": ["Post-surgery or recovery signal detected."],
                "risk_notes": ["Use general references only.", "Must prioritize physician guidance."],
            }
        )

    if not scored:
        scored.append(
            {
                "direction": "General nutrition habits support",
                "priority": Priority.medium.value,
                "confidence": Confidence.low.value,
                "trigger_reasons": ["Insufficient specific signals; generic support path selected."],
                "risk_notes": ["Collect more intake details before strong recommendations."],
            }
        )

    return scored


def build_assessment(customer: dict[str, Any], intake: dict[str, Any]) -> dict[str, Any]:
    red_flag, reasons = detect_red_flags(customer, intake)
    status = AssessmentStatus.needs_referral.value if red_flag else AssessmentStatus.assessed.value
    assessment = {
        "status": status,
        "requires_medical_referral": red_flag,
        "referral_reasons": reasons,
        "scenario_tags": infer_scenario_tags(customer, intake),
        "created_at": now_iso(),
    }
    return assessment


def infer_scenario_tags(customer: dict[str, Any], intake: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    complaints = " ".join(intake.get("complaints", [])).lower()
    if any(token in complaints for token in ["sleep", "insomnia"]):
        tags.append("sleep-support")
    if customer.get("recent_surgery") or "surgery" in " ".join(intake.get("special_events", [])).lower():
        tags.append("post-surgery")
    if not tags:
        tags.append("general")
    return tags


def build_recommendation(assessment: dict[str, Any], customer: dict[str, Any], intake: dict[str, Any]) -> dict[str, Any]:
    if assessment.get("requires_medical_referral"):
        return {
            "mode": "red-flag-general-reference",
            "requires_medical_referral": True,
            "advice_items": [
                {
                    "direction": "General nutrition reference only",
                    "priority": Priority.high.value,
                    "confidence": Confidence.low.value,
                    "trigger_reasons": assessment.get("referral_reasons", []),
                    "risk_notes": [
                        "Reference only. Not a diagnosis or treatment.",
                        "Seek physician advice first.",
                    ],
                    "general_reference": {
                        "foods": ["balanced protein sources", "hydration", "high-fiber vegetables"],
                        "vitamin_directions": ["vitamin D", "B-complex", "omega-3 (general awareness)"],
                    },
                }
            ],
            "created_at": now_iso(),
        }

    scored = score_nutrition_directions(customer, intake)
    return {
        "mode": "normal",
        "requires_medical_referral": False,
        "advice_items": scored,
        "created_at": now_iso(),
    }


def build_report(recommendation: dict[str, Any], customer: dict[str, Any], disclaimer_version: str) -> dict[str, Any]:
    common_disclaimer = {
        "version": disclaimer_version,
        "text": "This report is for nutrition support only and does not replace medical diagnosis or treatment. If symptoms persist or worsen, seek physician care promptly.",
    }

    customer_summary = {
        "age_group": customer.get("age_group"),
        "main_concern": customer.get("main_concern"),
    }

    customer_report = {
        "summary": customer_summary,
        "advice": recommendation.get("advice_items", []),
        "next_steps": ["Follow up in 2-4 weeks.", "Track symptom changes and adherence."],
        "disclaimer": common_disclaimer,
    }

    rep_script = {
        "opening": "This is nutrition support guidance and not a medical diagnosis.",
        "explainers": [
            "Explain each recommendation using trigger reasons.",
            "Avoid absolute efficacy claims.",
        ],
        "forbidden_phrases": [
            "This will definitely cure you.",
            "No need to see a doctor.",
            "You have a diagnosed disease.",
        ],
        "risk_handling": "If red flags are present, provide general reference only and recommend physician follow-up.",
    }

    return {"customer_report": customer_report, "rep_script": rep_script, "created_at": now_iso()}
