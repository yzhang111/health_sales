from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.auth import actor_from_auth_header, authenticate_user, ensure_default_users, get_user_by_username, issue_session_token
from app.config import load_question_flow, save_question_flow
from app.models import (
    AssessmentCreate,
    AdminUserCreate,
    AdminUserPasswordReset,
    AdminUserStatusPatch,
    ComplianceEventCreate,
    CustomerCreate,
    CustomerPatch,
    FollowUpClose,
    FollowUpCreate,
    FollowUpReassess,
    LoginRequest,
    RecommendationCreate,
    ReportCreate,
    now_iso,
)
from app.services import build_assessment, build_recommendation, build_report
from app.security import hash_password
from app.store import STORE

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_default_users()
    yield


app = FastAPI(title="Nutrition Assistant API", version="1.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def ok(data: Any, meta: dict[str, Any] | None = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"data": data, "meta": meta or {}})


def fail(code: str, message: str, details: list[dict[str, Any]] | None = None, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details or []}},
    )


def resolve_actor_id(authorization: str | None, fallback_actor_id: str) -> str:
    actor = actor_from_auth_header(authorization)
    if actor:
        return actor["actor_id"]
    return fallback_actor_id


def require_admin(authorization: str | None) -> dict[str, Any] | JSONResponse:
    actor = actor_from_auth_header(authorization)
    if not actor:
        return fail("unauthorized", "Admin token is required", status_code=401)
    if actor["role"] != "admin":
        return fail("forbidden", "Admin role required", status_code=403)
    return actor


def require_login(authorization: str | None) -> dict[str, Any] | JSONResponse:
    actor = actor_from_auth_header(authorization)
    if not actor:
        return fail("unauthorized", "Login token required", status_code=401)
    return actor


def get_or_404(table: str, resource_id: str, resource_name: str) -> dict[str, Any] | JSONResponse:
    obj = STORE.get(table, resource_id)
    if not obj:
        return fail("not_found", f"{resource_name} not found", status_code=404)
    return obj


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/v1/health")
def health() -> JSONResponse:
    return ok({"status": "ok", "time": now_iso(), "storage": "sqlite"})


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest) -> JSONResponse:
    user = authenticate_user(payload.username, payload.password)
    if not user:
        return fail("invalid_credentials", "Invalid username/password", status_code=401)
    token = issue_session_token(username=user["username"], actor_id=user["actor_id"], role=user["role"])
    return ok({"token": token, "actor_id": user["actor_id"], "role": user["role"], "username": user["username"]})


@app.get("/api/v1/admin/users")
def list_admin_users(authorization: str | None = Header(default=None)) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    users = STORE.list("users")
    sanitized = [
        {
            "id": u["id"],
            "username": u["username"],
            "role": u["role"],
            "actor_id": u["actor_id"],
            "is_active": u.get("is_active", True),
            "created_at": u.get("created_at"),
        }
        for u in users
    ]
    return ok(sanitized, meta={"count": len(sanitized)})


@app.post("/api/v1/admin/users")
def create_admin_user(payload: AdminUserCreate, authorization: str | None = Header(default=None)) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    if payload.role not in {"admin", "sales"}:
        return fail("validation_error", "role must be admin or sales", status_code=422)
    if get_user_by_username(payload.username):
        return fail("conflict", "username already exists", status_code=409)

    user_id = STORE.new_id("usr")
    record = {
        "id": user_id,
        "username": payload.username,
        "role": payload.role,
        "actor_id": payload.actor_id or f"{payload.role}_{user_id[-4:]}",
        "is_active": True,
        "password_hash": hash_password(payload.password),
        "created_at": now_iso(),
    }
    STORE.upsert("users", user_id, record)
    STORE.audit(actor["actor_id"], "create", "user", user_id, "admin_create_user", {"username": payload.username, "role": payload.role})
    return ok(
        {
            "id": record["id"],
            "username": record["username"],
            "role": record["role"],
            "actor_id": record["actor_id"],
            "is_active": record["is_active"],
            "created_at": record["created_at"],
        },
        status_code=201,
    )


@app.patch("/api/v1/admin/users/{user_id}/status")
def patch_admin_user_status(
    user_id: str, payload: AdminUserStatusPatch, authorization: str | None = Header(default=None)
) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    user = STORE.get("users", user_id)
    if not user:
        return fail("not_found", "user not found", status_code=404)
    user["is_active"] = payload.is_active
    user["updated_at"] = now_iso()
    STORE.upsert("users", user_id, user)
    STORE.audit(actor["actor_id"], "update", "user", user_id, "admin_patch_user_status", {"is_active": payload.is_active})
    return ok({"id": user["id"], "username": user["username"], "is_active": user["is_active"]})


@app.patch("/api/v1/admin/users/{user_id}/password")
def patch_admin_user_password(
    user_id: str, payload: AdminUserPasswordReset, authorization: str | None = Header(default=None)
) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    if len(payload.new_password) < 8:
        return fail("validation_error", "new_password must be at least 8 chars", status_code=422)
    user = STORE.get("users", user_id)
    if not user:
        return fail("not_found", "user not found", status_code=404)
    user["password_hash"] = hash_password(payload.new_password)
    user["updated_at"] = now_iso()
    STORE.upsert("users", user_id, user)
    STORE.audit(actor["actor_id"], "update", "user", user_id, "admin_reset_user_password", {"username": user["username"]})
    return ok({"id": user["id"], "username": user["username"], "password_reset": True})


@app.get("/api/v1/question-flow")
def get_question_flow() -> JSONResponse:
    return ok(load_question_flow())


@app.put("/api/v1/question-flow")
def put_question_flow(payload: dict[str, Any], authorization: str | None = Header(default=None)) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    if "sections" not in payload or not isinstance(payload["sections"], list):
        return fail("validation_error", "sections(list) is required", status_code=422)
    saved = save_question_flow(payload)
    STORE.audit(actor["actor_id"], "update", "question_flow", "global", "question_flow_update", saved)
    return ok(saved)


@app.post("/api/v1/customers")
def create_customer(payload: CustomerCreate, authorization: str | None = Header(default=None)) -> JSONResponse:
    customer_id = STORE.new_id("cus")
    actor_id = resolve_actor_id(authorization, payload.actor_id)
    record = payload.model_dump()
    record.update({"id": customer_id, "created_at": now_iso(), "updated_at": now_iso()})
    STORE.upsert("customers", customer_id, record)
    STORE.audit(actor_id, "create", "customer", customer_id, "customer_create", record)
    return ok(record, status_code=201)


@app.get("/api/v1/customers/{customer_id}")
def get_customer(customer_id: str) -> JSONResponse:
    obj = get_or_404("customers", customer_id, "Customer")
    if isinstance(obj, JSONResponse):
        return obj
    return ok(obj)


@app.patch("/api/v1/customers/{customer_id}")
def patch_customer(customer_id: str, payload: CustomerPatch, authorization: str | None = Header(default=None)) -> JSONResponse:
    obj = get_or_404("customers", customer_id, "Customer")
    if isinstance(obj, JSONResponse):
        return obj
    updates = payload.model_dump(exclude_none=True)
    actor_id = resolve_actor_id(authorization, updates.pop("actor_id"))
    obj.update(updates)
    obj["updated_at"] = now_iso()
    STORE.upsert("customers", customer_id, obj)
    STORE.audit(actor_id, "update", "customer", customer_id, "customer_patch", obj)
    return ok(obj)


@app.post("/api/v1/assessments")
def create_assessment(payload: AssessmentCreate, authorization: str | None = Header(default=None)) -> JSONResponse:
    customer = get_or_404("customers", payload.customer_id, "Customer")
    if isinstance(customer, JSONResponse):
        return customer

    actor_id = resolve_actor_id(authorization, payload.actor_id)
    intake = payload.intake_answers.model_dump()
    assessment_core = build_assessment(customer, intake)
    assessment_id = STORE.new_id("asm")
    record = {
        "id": assessment_id,
        "customer_id": payload.customer_id,
        "intake_answers": intake,
        **assessment_core,
        "created_by": actor_id,
    }
    STORE.upsert("assessments", assessment_id, record)
    STORE.audit(actor_id, "create", "assessment", assessment_id, "assessment_create", record)
    return ok(record, status_code=201)


@app.get("/api/v1/assessments/{assessment_id}")
def get_assessment(assessment_id: str) -> JSONResponse:
    obj = get_or_404("assessments", assessment_id, "Assessment")
    if isinstance(obj, JSONResponse):
        return obj
    return ok(obj)


@app.post("/api/v1/assessments/{assessment_id}/re-evaluate")
def reevaluate_assessment(
    assessment_id: str, actor_id: str = Query(...), authorization: str | None = Header(default=None)
) -> JSONResponse:
    assessment = get_or_404("assessments", assessment_id, "Assessment")
    if isinstance(assessment, JSONResponse):
        return assessment
    customer = get_or_404("customers", assessment["customer_id"], "Customer")
    if isinstance(customer, JSONResponse):
        return customer

    latest = build_assessment(customer, assessment["intake_answers"])
    assessment.update(latest)
    assessment["re_evaluated_at"] = now_iso()
    STORE.upsert("assessments", assessment_id, assessment)
    final_actor_id = resolve_actor_id(authorization, actor_id)
    STORE.audit(final_actor_id, "update", "assessment", assessment_id, "assessment_re_evaluate", assessment)
    return ok(assessment)


@app.post("/api/v1/recommendations")
def create_recommendation(payload: RecommendationCreate, authorization: str | None = Header(default=None)) -> JSONResponse:
    assessment = get_or_404("assessments", payload.assessment_id, "Assessment")
    if isinstance(assessment, JSONResponse):
        return assessment
    customer = get_or_404("customers", assessment["customer_id"], "Customer")
    if isinstance(customer, JSONResponse):
        return customer

    actor_id = resolve_actor_id(authorization, payload.actor_id)
    recommendation_id = STORE.new_id("rec")
    rec = build_recommendation(assessment, customer, assessment["intake_answers"])
    record = {
        "id": recommendation_id,
        "assessment_id": payload.assessment_id,
        "customer_id": assessment["customer_id"],
        **rec,
        "created_by": actor_id,
    }
    STORE.upsert("recommendations", recommendation_id, record)
    STORE.audit(actor_id, "create", "recommendation", recommendation_id, "recommendation_create", record)
    return ok(record, status_code=201)


@app.get("/api/v1/recommendations/{recommendation_id}")
def get_recommendation(recommendation_id: str) -> JSONResponse:
    obj = get_or_404("recommendations", recommendation_id, "Recommendation")
    if isinstance(obj, JSONResponse):
        return obj
    return ok(obj)


@app.post("/api/v1/reports")
def create_report(payload: ReportCreate, authorization: str | None = Header(default=None)) -> JSONResponse:
    recommendation = get_or_404("recommendations", payload.recommendation_id, "Recommendation")
    if isinstance(recommendation, JSONResponse):
        return recommendation
    customer = get_or_404("customers", recommendation["customer_id"], "Customer")
    if isinstance(customer, JSONResponse):
        return customer

    actor_id = resolve_actor_id(authorization, payload.actor_id)
    report_id = STORE.new_id("rpt")
    content = build_report(recommendation, customer, payload.disclaimer_version)
    record = {
        "id": report_id,
        "status": "ready",
        "recommendation_id": payload.recommendation_id,
        "customer_id": recommendation["customer_id"],
        **content,
        "created_by": actor_id,
    }
    STORE.upsert("reports", report_id, record)
    STORE.audit(actor_id, "create", "report", report_id, "report_create", record)
    return ok(record, status_code=202)


@app.get("/api/v1/reports/{report_id}")
def get_report(report_id: str) -> JSONResponse:
    obj = get_or_404("reports", report_id, "Report")
    if isinstance(obj, JSONResponse):
        return obj
    return ok(obj)


@app.post("/api/v1/reports/{report_id}/export")
def export_report(report_id: str, authorization: str | None = Header(default=None)) -> JSONResponse:
    actor = require_login(authorization)
    if isinstance(actor, JSONResponse):
        return actor

    report = get_or_404("reports", report_id, "Report")
    if isinstance(report, JSONResponse):
        return report

    export_path = EXPORT_DIR / f"{report_id}.json"
    payload = {"exported_at": now_iso(), "exported_by": actor["actor_id"], "report": report}
    export_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    STORE.audit(actor["actor_id"], "export", "report", report_id, "report_export_json", {"path": str(export_path)})
    return ok({"report_id": report_id, "file_path": str(export_path)})


@app.get("/api/v1/exports")
def list_exports(authorization: str | None = Header(default=None)) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    files = sorted(
        [p for p in EXPORT_DIR.iterdir() if p.is_file() and p.suffix in {".json", ".md"}],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    rows = [
        {
            "filename": p.name,
            "path": str(p),
            "size_bytes": p.stat().st_size,
            "updated_at": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
        }
        for p in files
    ]
    return ok(rows, meta={"count": len(rows)})


@app.get("/api/v1/exports/{filename}")
def download_export(filename: str, authorization: str | None = Header(default=None)):
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    safe_name = Path(filename).name
    if safe_name != filename or Path(safe_name).suffix not in {".json", ".md"}:
        return fail("validation_error", "invalid filename", status_code=422)
    target = EXPORT_DIR / safe_name
    if not target.exists():
        return fail("not_found", "export file not found", status_code=404)
    return FileResponse(target, media_type="application/json", filename=safe_name)


@app.post("/api/v1/follow-ups")
def create_followup(payload: FollowUpCreate, authorization: str | None = Header(default=None)) -> JSONResponse:
    if payload.due_in_weeks < 1 or payload.due_in_weeks > 8:
        return fail("validation_error", "due_in_weeks must be between 1 and 8", status_code=422)
    customer = get_or_404("customers", payload.customer_id, "Customer")
    if isinstance(customer, JSONResponse):
        return customer

    actor_id = resolve_actor_id(authorization, payload.actor_id)
    followup_id = STORE.new_id("flw")
    record = {
        "id": followup_id,
        "customer_id": payload.customer_id,
        "recommendation_id": payload.recommendation_id,
        "due_in_weeks": payload.due_in_weeks,
        "notes": payload.notes,
        "status": "scheduled",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "created_by": actor_id,
    }
    STORE.upsert("followups", followup_id, record)
    STORE.audit(actor_id, "create", "followup", followup_id, "followup_create", record)
    return ok(record, status_code=201)


@app.get("/api/v1/follow-ups/{followup_id}")
def get_followup(followup_id: str) -> JSONResponse:
    obj = get_or_404("followups", followup_id, "Follow-up")
    if isinstance(obj, JSONResponse):
        return obj
    return ok(obj)


@app.post("/api/v1/follow-ups/{followup_id}/close")
def close_followup(followup_id: str, payload: FollowUpClose, authorization: str | None = Header(default=None)) -> JSONResponse:
    followup = get_or_404("followups", followup_id, "Follow-up")
    if isinstance(followup, JSONResponse):
        return followup
    followup["status"] = "closed"
    followup["outcome_notes"] = payload.outcome_notes
    followup["symptoms_improved"] = payload.symptoms_improved
    followup["updated_at"] = now_iso()
    STORE.upsert("followups", followup_id, followup)
    actor_id = resolve_actor_id(authorization, payload.actor_id)
    STORE.audit(actor_id, "update", "followup", followup_id, "followup_close", followup)
    return ok(followup)


@app.post("/api/v1/follow-ups/{followup_id}/re-assess")
def reassess_after_followup(
    followup_id: str, payload: FollowUpReassess, authorization: str | None = Header(default=None)
) -> JSONResponse:
    followup = get_or_404("followups", followup_id, "Follow-up")
    if isinstance(followup, JSONResponse):
        return followup
    if followup.get("status") != "closed":
        return fail("state_conflict", "Follow-up must be closed before re-assessment", status_code=409)

    recommendation_id = followup.get("recommendation_id")
    if not recommendation_id:
        return fail("state_conflict", "Follow-up has no recommendation link", status_code=409)

    recommendation = get_or_404("recommendations", recommendation_id, "Recommendation")
    if isinstance(recommendation, JSONResponse):
        return recommendation
    assessment = get_or_404("assessments", recommendation["assessment_id"], "Assessment")
    if isinstance(assessment, JSONResponse):
        return assessment
    customer = get_or_404("customers", followup["customer_id"], "Customer")
    if isinstance(customer, JSONResponse):
        return customer

    actor_id = resolve_actor_id(authorization, payload.actor_id)
    original_intake = assessment["intake_answers"]
    new_intake = {
        "complaints": list(original_intake.get("complaints", [])) + list(payload.extra_complaints),
        "lifestyle_answers": original_intake.get("lifestyle_answers", {}),
        "special_events": original_intake.get("special_events", []),
        "meds_and_contraindications": original_intake.get("meds_and_contraindications", []),
        "goals": payload.updated_goals or original_intake.get("goals", []),
    }

    assessment_core = build_assessment(customer, new_intake)
    new_assessment_id = STORE.new_id("asm")
    new_assessment = {
        "id": new_assessment_id,
        "customer_id": followup["customer_id"],
        "intake_answers": new_intake,
        **assessment_core,
        "created_by": actor_id,
        "reassessed_from_followup_id": followup_id,
    }
    STORE.upsert("assessments", new_assessment_id, new_assessment)
    STORE.audit(actor_id, "create", "assessment", new_assessment_id, "followup_re_assessment", new_assessment)

    new_recommendation_id = STORE.new_id("rec")
    rec_core = build_recommendation(new_assessment, customer, new_intake)
    new_recommendation = {
        "id": new_recommendation_id,
        "assessment_id": new_assessment_id,
        "customer_id": followup["customer_id"],
        **rec_core,
        "created_by": actor_id,
        "from_followup_id": followup_id,
    }
    STORE.upsert("recommendations", new_recommendation_id, new_recommendation)
    STORE.audit(actor_id, "create", "recommendation", new_recommendation_id, "followup_re_recommendation", new_recommendation)

    followup["reassessed_assessment_id"] = new_assessment_id
    followup["reassessed_recommendation_id"] = new_recommendation_id
    followup["updated_at"] = now_iso()
    STORE.upsert("followups", followup_id, followup)
    STORE.audit(actor_id, "update", "followup", followup_id, "followup_link_reassessment", followup)

    return ok(
        {
            "followup_id": followup_id,
            "new_assessment_id": new_assessment_id,
            "new_recommendation_id": new_recommendation_id,
            "assessment": new_assessment,
            "recommendation": new_recommendation,
        }
    )


@app.post("/api/v1/compliance-events")
def create_compliance_event(payload: ComplianceEventCreate, authorization: str | None = Header(default=None)) -> JSONResponse:
    actor_id = resolve_actor_id(authorization, payload.actor_id)
    event_id = STORE.new_id("cmp")
    event = {
        "id": event_id,
        "customer_id": payload.customer_id,
        "event_type": payload.event_type,
        "reason": payload.reason,
        "payload": payload.payload,
        "created_by": actor_id,
        "created_at": now_iso(),
    }
    STORE.upsert("compliance_events", event_id, event)
    STORE.audit(actor_id, "create", "compliance_event", event_id, "compliance_event_create", event)
    return ok(event, status_code=201)


@app.get("/api/v1/compliance-events")
def list_compliance_events(customer_id: str | None = Query(default=None)) -> JSONResponse:
    rows = STORE.list("compliance_events")
    if customer_id:
        rows = [row for row in rows if row["customer_id"] == customer_id]
    return ok(rows, meta={"count": len(rows)})


@app.get("/api/v1/audit-logs")
def list_audit_logs(limit: int = Query(default=100, ge=1, le=500), authorization: str | None = Header(default=None)) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    rows = STORE.list_audit(limit=limit)
    return ok(rows, meta={"count": len(rows)})


def build_metrics_snapshot() -> dict[str, Any]:
    customers = STORE.list("customers")
    assessments = STORE.list("assessments")
    recommendations = STORE.list("recommendations")
    reports = STORE.list("reports")
    followups = STORE.list("followups")

    red_flags = [a for a in assessments if a.get("requires_medical_referral")]
    rec_red = [r for r in recommendations if r.get("mode") == "red-flag-general-reference"]
    rec_normal = [r for r in recommendations if r.get("mode") == "normal"]
    followup_closed = [f for f in followups if f.get("status") == "closed"]
    followup_scheduled = [f for f in followups if f.get("status") == "scheduled"]
    improved = [f for f in followup_closed if f.get("symptoms_improved") is True]

    def rate(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 4)

    return {
        "totals": {
            "customers": len(customers),
            "assessments": len(assessments),
            "recommendations": len(recommendations),
            "reports": len(reports),
            "followups": len(followups),
        },
        "risk": {
            "red_flag_count": len(red_flags),
            "red_flag_rate": rate(len(red_flags), len(assessments)),
            "red_flag_recommendation_count": len(rec_red),
        },
        "recommendation_modes": {
            "normal": len(rec_normal),
            "red_flag_general_reference": len(rec_red),
        },
        "followup": {
            "scheduled": len(followup_scheduled),
            "closed": len(followup_closed),
            "close_rate": rate(len(followup_closed), len(followups)),
            "improved_count": len(improved),
            "improved_rate_on_closed": rate(len(improved), len(followup_closed)),
        },
    }


@app.get("/api/v1/metrics/summary")
def metrics_summary(authorization: str | None = Header(default=None)) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor
    return ok(build_metrics_snapshot())


@app.post("/api/v1/ops/export-summary")
def export_ops_summary(authorization: str | None = Header(default=None)) -> JSONResponse:
    actor = require_admin(authorization)
    if isinstance(actor, JSONResponse):
        return actor

    snapshot = build_metrics_snapshot()
    recent_audits = STORE.list_audit(limit=20)
    ts = now_iso().replace(":", "-")
    filename = f"ops_summary_{ts}.md"
    target = EXPORT_DIR / filename

    lines = [
        "# Nutrition Assistant Ops Summary\n",
        f"\nGenerated at: {now_iso()}\n",
        f"\nGenerated by: {actor['actor_id']}\n",
        "\n## Totals\n",
        f"- Customers: {snapshot['totals']['customers']}\n",
        f"- Assessments: {snapshot['totals']['assessments']}\n",
        f"- Recommendations: {snapshot['totals']['recommendations']}\n",
        f"- Reports: {snapshot['totals']['reports']}\n",
        f"- Follow-ups: {snapshot['totals']['followups']}\n",
        "\n## Risk\n",
        f"- Red flags: {snapshot['risk']['red_flag_count']}\n",
        f"- Red flag rate: {round(snapshot['risk']['red_flag_rate'] * 100, 2)}%\n",
        f"- Red-flag general reference recommendations: {snapshot['risk']['red_flag_recommendation_count']}\n",
        "\n## Follow-up Outcomes\n",
        f"- Scheduled: {snapshot['followup']['scheduled']}\n",
        f"- Closed: {snapshot['followup']['closed']}\n",
        f"- Close rate: {round(snapshot['followup']['close_rate'] * 100, 2)}%\n",
        f"- Improved count: {snapshot['followup']['improved_count']}\n",
        f"- Improvement rate on closed: {round(snapshot['followup']['improved_rate_on_closed'] * 100, 2)}%\n",
        "\n## Recent Audit Events (Top 20)\n",
    ]
    if recent_audits:
        for row in recent_audits:
            lines.append(
                f"- {row['timestamp']} | {row['actor_id']} | {row['action']} "
                f"{row['resource']}:{row['resource_id']} ({row['reason']})\n"
            )
    else:
        lines.append("- No audit events yet.\n")

    target.write_text("".join(lines), encoding="utf-8")
    STORE.audit(actor["actor_id"], "export", "ops_summary", filename, "ops_summary_export_md", {"path": str(target)})
    return ok({"file_path": str(target), "filename": filename, "snapshot": snapshot})
