from __future__ import annotations

from pathlib import Path
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import app

def login(client: TestClient, role: str, password: str) -> str:
    res = client.post("/api/v1/auth/login", json={"username": role, "password": password})
    assert res.status_code == 200
    return res.json()["data"]["token"]


def test_role_and_flow_and_export() -> None:
    with TestClient(app) as client:
        admin_token = login(client, "admin", "admin123")
        sales_token = login(client, "sales", "sales123")

        # Admin user management.
        users_before = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert users_before.status_code == 200
        assert users_before.json()["meta"]["count"] >= 2

        unique_username = f"sales_{uuid4().hex[:8]}"
        unique_password = "sales2123"
        create_user = client.post(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"username": unique_username, "password": unique_password, "role": "sales"},
        )
        assert create_user.status_code == 201
        user_id = create_user.json()["data"]["id"]

        login_new = client.post("/api/v1/auth/login", json={"username": unique_username, "password": unique_password})
        assert login_new.status_code == 200

        disable_user = client.patch(
            f"/api/v1/admin/users/{user_id}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"is_active": False},
        )
        assert disable_user.status_code == 200
        assert disable_user.json()["data"]["is_active"] is False

        login_disabled = client.post("/api/v1/auth/login", json={"username": unique_username, "password": unique_password})
        assert login_disabled.status_code == 401

        enable_user = client.patch(
            f"/api/v1/admin/users/{user_id}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"is_active": True},
        )
        assert enable_user.status_code == 200

        reset_pwd = client.patch(
            f"/api/v1/admin/users/{user_id}/password",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"new_password": "resetpass123"},
        )
        assert reset_pwd.status_code == 200

        old_pwd_login = client.post("/api/v1/auth/login", json={"username": unique_username, "password": unique_password})
        assert old_pwd_login.status_code == 401
        new_pwd_login = client.post("/api/v1/auth/login", json={"username": unique_username, "password": "resetpass123"})
        assert new_pwd_login.status_code == 200

        # Sales cannot update question flow.
        denied = client.put(
            "/api/v1/question-flow",
            headers={"Authorization": f"Bearer {sales_token}"},
            json={"version": "v-test", "sections": []},
        )
        assert denied.status_code == 403

        # Admin can update question flow.
        updated = client.put(
            "/api/v1/question-flow",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "version": "v-test",
                "sections": [{"key": "main", "title": "Main", "required": True, "questions": ["Q?"]}],
            },
        )
        assert updated.status_code == 200

        # Normal flow.
        customer = client.post(
            "/api/v1/customers",
            headers={"Authorization": f"Bearer {sales_token}"},
            json={
                "actor_id": "x",
                "age_group": "30-39",
                "main_concern": "sleep",
                "recent_surgery": False,
                "medications": [],
                "allergies_or_contraindications": [],
            },
        )
        assert customer.status_code == 201
        cid = customer.json()["data"]["id"]

        assessment = client.post(
        "/api/v1/assessments",
        headers={"Authorization": f"Bearer {sales_token}"},
        json={
            "actor_id": "x",
            "customer_id": cid,
            "intake_answers": {
                "complaints": ["insomnia"],
                "lifestyle_answers": {"stress": "high"},
                "special_events": [],
                "meds_and_contraindications": [],
                "goals": ["sleep"],
            },
        },
    )
        assert assessment.status_code == 201
        aid = assessment.json()["data"]["id"]

        recommendation = client.post(
        "/api/v1/recommendations",
        headers={"Authorization": f"Bearer {sales_token}"},
        json={"actor_id": "x", "assessment_id": aid},
    )
        assert recommendation.status_code == 201
        rid = recommendation.json()["data"]["id"]

        report = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {sales_token}"},
        json={"actor_id": "x", "recommendation_id": rid, "disclaimer_version": "v1.0"},
    )
        assert report.status_code == 202
        report_id = report.json()["data"]["id"]

    # Export requires login.
        export_unauth = client.post(f"/api/v1/reports/{report_id}/export")
        assert export_unauth.status_code == 401

        export_ok = client.post(
        f"/api/v1/reports/{report_id}/export",
        headers={"Authorization": f"Bearer {sales_token}"},
    )
        assert export_ok.status_code == 200
        export_path = Path(export_ok.json()["data"]["file_path"])
        assert export_path.exists()

        export_list_sales = client.get("/api/v1/exports", headers={"Authorization": f"Bearer {sales_token}"})
        assert export_list_sales.status_code == 403
        export_list_admin = client.get("/api/v1/exports", headers={"Authorization": f"Bearer {admin_token}"})
        assert export_list_admin.status_code == 200
        assert export_list_admin.json()["meta"]["count"] >= 1
        filename = export_list_admin.json()["data"][0]["filename"]

        export_download = client.get(f"/api/v1/exports/{filename}", headers={"Authorization": f"Bearer {admin_token}"})
        assert export_download.status_code == 200
        assert "application" in export_download.headers.get("content-type", "")

    # follow-up close and re-assess
        followup = client.post(
        "/api/v1/follow-ups",
        headers={"Authorization": f"Bearer {sales_token}"},
        json={
            "actor_id": "x",
            "customer_id": cid,
            "recommendation_id": rid,
            "due_in_weeks": 2,
            "notes": "initial follow-up",
        },
    )
        assert followup.status_code == 201
        fid = followup.json()["data"]["id"]

        closed = client.post(
        f"/api/v1/follow-ups/{fid}/close",
        headers={"Authorization": f"Bearer {sales_token}"},
        json={"actor_id": "x", "outcome_notes": "better sleep", "symptoms_improved": True},
    )
        assert closed.status_code == 200

        reassess = client.post(
        f"/api/v1/follow-ups/{fid}/re-assess",
        headers={"Authorization": f"Bearer {sales_token}"},
        json={"actor_id": "x", "extra_complaints": ["still wakes up once"], "updated_goals": ["sleep deeper"]},
    )
        assert reassess.status_code == 200
        assert reassess.json()["data"]["new_assessment_id"].startswith("asm_")
        assert reassess.json()["data"]["new_recommendation_id"].startswith("rec_")

    # Admin audit access.
        logs = client.get("/api/v1/audit-logs?limit=20", headers={"Authorization": f"Bearer {admin_token}"})
        assert logs.status_code == 200
        assert logs.json()["meta"]["count"] >= 1

    # Metrics summary (admin only)
        denied_metrics = client.get("/api/v1/metrics/summary", headers={"Authorization": f"Bearer {sales_token}"})
        assert denied_metrics.status_code == 403
        metrics = client.get("/api/v1/metrics/summary", headers={"Authorization": f"Bearer {admin_token}"})
        assert metrics.status_code == 200
        assert "totals" in metrics.json()["data"]

    # Ops summary export (admin only)
        denied_ops = client.post("/api/v1/ops/export-summary", headers={"Authorization": f"Bearer {sales_token}"})
        assert denied_ops.status_code == 403
        ops = client.post("/api/v1/ops/export-summary", headers={"Authorization": f"Bearer {admin_token}"})
        assert ops.status_code == 200
        ops_filename = ops.json()["data"]["filename"]
        assert ops_filename.endswith(".md")

    # Download the exported ops summary
        ops_download = client.get(f"/api/v1/exports/{ops_filename}", headers={"Authorization": f"Bearer {admin_token}"})
        assert ops_download.status_code == 200
