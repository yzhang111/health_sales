from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Priority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class AssessmentStatus(str, Enum):
    draft_intake = "draft_intake"
    intake_completed = "intake_completed"
    risk_screened = "risk_screened"
    needs_referral = "needs_referral"
    assessed = "assessed"


class CustomerCreate(BaseModel):
    actor_id: str = Field(..., description="Who performed the write action")
    age_group: str
    gender: str | None = None
    main_concern: str
    lifestyle: dict[str, Any] = Field(default_factory=dict)
    recent_surgery: bool
    surgery_note: str | None = None
    medications: list[str] = Field(default_factory=list)
    allergies_or_contraindications: list[str] = Field(default_factory=list)
    contact: str | None = None


class CustomerPatch(BaseModel):
    actor_id: str
    age_group: str | None = None
    gender: str | None = None
    main_concern: str | None = None
    lifestyle: dict[str, Any] | None = None
    recent_surgery: bool | None = None
    surgery_note: str | None = None
    medications: list[str] | None = None
    allergies_or_contraindications: list[str] | None = None
    contact: str | None = None


class IntakeAnswers(BaseModel):
    complaints: list[str] = Field(default_factory=list)
    lifestyle_answers: dict[str, str] = Field(default_factory=dict)
    special_events: list[str] = Field(default_factory=list)
    meds_and_contraindications: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)


class AssessmentCreate(BaseModel):
    actor_id: str
    customer_id: str
    intake_answers: IntakeAnswers


class RecommendationCreate(BaseModel):
    actor_id: str
    assessment_id: str


class ReportCreate(BaseModel):
    actor_id: str
    recommendation_id: str
    disclaimer_version: str = "v1.0"


class FollowUpCreate(BaseModel):
    actor_id: str
    customer_id: str
    recommendation_id: str | None = None
    due_in_weeks: int = 2
    notes: str | None = None


class FollowUpClose(BaseModel):
    actor_id: str
    outcome_notes: str
    symptoms_improved: bool | None = None


class FollowUpReassess(BaseModel):
    actor_id: str
    extra_complaints: list[str] = Field(default_factory=list)
    updated_goals: list[str] = Field(default_factory=list)


class ComplianceEventCreate(BaseModel):
    actor_id: str
    customer_id: str
    event_type: str
    reason: str
    payload: dict[str, Any] = Field(default_factory=dict)


class LoginRequest(BaseModel):
    username: str
    password: str


class AdminUserCreate(BaseModel):
    username: str
    password: str
    role: str
    actor_id: str | None = None


class AdminUserStatusPatch(BaseModel):
    is_active: bool


class AdminUserPasswordReset(BaseModel):
    new_password: str
