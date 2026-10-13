"""GripWise Saathi — Automated test suite for mechanic advocacy & engagement module.

Tests cover:
- Persistence of mechanic profile & completion percentage calculation
- Learning Hub: modules listing, content retrieval, quiz scoring, passing threshold
- Idempotency: duplicate quiz submissions do not award duplicate points or badges
- Real metrics & scoring rules: points aggregation and tier transitions (Bronze -> Silver -> Gold -> Master)
- Verifiable badge awards: profile completion badge, learning pioneer badge, safety advocate badge
- Consent-aware customer referrals: creation, status transitions, privacy protection
- Role authorization: riders cannot access mechanic endpoints (403 Forbidden)
- Mechanic isolation: mechanics cannot modify each other's referrals
- Eurogrip TORQ Challenge 4.0 proposed initiatives endpoint & disclaimers
"""
import pytest
import uuid
from httpx import AsyncClient
from backend.config import settings


@pytest.fixture
async def mechanic_token_headers(client: AsyncClient):
    # Register unique mechanic
    uid = uuid.uuid4().hex[:6]
    res = await client.post("/api/auth/register", json={
        "display_name": f"Mechanic {uid}",
        "email": f"mech_{uid}@test.com",
        "role": "MECHANIC",
        "password": "Password123!",
        "workshop_name": f"Workshop {uid}",
        "workshop_city": "Pune"
    })
    assert res.status_code in [200, 201], res.text
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def mechanic_b_headers(client: AsyncClient):
    # Register second unique mechanic
    uid = uuid.uuid4().hex[:6]
    res = await client.post("/api/auth/register", json={
        "display_name": f"Mechanic B {uid}",
        "email": f"mech_b_{uid}@test.com",
        "role": "MECHANIC",
        "password": "Password123!",
        "workshop_name": f"Workshop B {uid}",
        "workshop_city": "Mumbai"
    })
    assert res.status_code in [200, 201], res.text
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def rider_token_headers(client: AsyncClient):
    # Register unique rider
    uid = uuid.uuid4().hex[:6]
    res = await client.post("/api/auth/register", json={
        "display_name": f"Rider {uid}",
        "email": f"rider_{uid}@test.com",
        "role": "RIDER",
        "password": "Password123!"
    })
    assert res.status_code in [200, 201], res.text
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_saathi_dashboard_empty_state(client: AsyncClient, mechanic_token_headers):
    """Test initial fresh dashboard returns 0 points, Bronze tier, and empty state metrics."""
    res = await client.get("/api/saathi/dashboard", headers=mechanic_token_headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert "Mechanic" in data["display_name"]
    assert "Workshop" in data["workshop_name"]
    assert data["total_points"] == 0
    assert data["tier"] == "Bronze Saathi"
    assert data["completed_modules_count"] == 0
    assert data["verified_findings_count"] == 0
    assert data["recorded_services_count"] == 0
    assert data["total_referrals_count"] == 0
    assert data["case_study_context"]["program_name"] == "Mechanic Growth"
    assert "partnership" not in data["case_study_context"]["disclaimer"].lower()


@pytest.mark.asyncio
async def test_profile_completion_indicator_and_update(client: AsyncClient, mechanic_token_headers):
    """Test updating mechanic profile fields increases profile completeness indicator."""
    # 1. Initial profile check
    res = await client.get("/api/saathi/profile", headers=mechanic_token_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    initial_pct = data["completion_percent"]
    assert initial_pct < 80  # missing years_experience, address, specialization, bio

    # 2. Update profile with detailed information
    update_res = await client.put("/api/saathi/profile", json={
        "years_experience": 8,
        "specialization": "Two-Wheeler Tyre & Alignment Specialist",
        "workshop_address": "Shop 4, MG Road Corner, Pune",
        "phone": "+91 98765 43210",
        "bio": "Certified mechanic with 8 years experience in tubeless tyre repair and safety checks.",
        "certifications": ["Automotive Tyre Care Certificate"]
    }, headers=mechanic_token_headers)
    assert update_res.status_code == 200
    updated_data = update_res.json()["data"]
    assert updated_data["completion_percent"] == 100
    assert updated_data["years_experience"] == 8
    assert updated_data["specialization"] == "Two-Wheeler Tyre & Alignment Specialist"

    # 3. Check dashboard awards BADGE_WELCOME (Profile completeness >= 80%)
    dash_res = await client.get("/api/saathi/dashboard", headers=mechanic_token_headers)
    dash_data = dash_res.json()["data"]
    earned_badge_ids = [b["id"] for b in dash_data["earned_badges"]]
    assert "BADGE_WELCOME" in earned_badge_ids


@pytest.mark.asyncio
async def test_learning_hub_module_list_and_detail(client: AsyncClient, mechanic_token_headers):
    """Test listing learning modules and retrieving content markdown with quiz questions."""
    # 1. List modules
    res = await client.get("/api/saathi/learning/modules", headers=mechanic_token_headers)
    assert res.status_code == 200
    modules = res.json()["data"]["modules"]
    assert len(modules) >= 5
    codes = [m["module_code"] for m in modules]
    assert "MOD-01" in codes
    assert "MOD-05" in codes

    # 2. Get detail for MOD-01
    detail_res = await client.get("/api/saathi/learning/modules/mod-tread-wear", headers=mechanic_token_headers)
    assert detail_res.status_code == 200
    mod = detail_res.json()["data"]
    assert mod["title"] == "Tread Wear Patterns, TWI & Safety Limits"
    assert "Tread Wear Indicators" in mod["content_markdown"]
    assert len(mod["quiz_questions"]) == 3
    assert "ISO" in mod["technical_source"]


@pytest.mark.asyncio
async def test_quiz_scoring_and_idempotent_points(client: AsyncClient, mechanic_token_headers):
    """Test submitting quiz answers: pass threshold, point awards, and idempotency on retake."""
    # 1. Submit failing quiz (0 correct)
    fail_res = await client.post("/api/saathi/learning/modules/mod-tread-wear/quiz", json={
        "answers": [0, 1, 0]  # wrong answers
    }, headers=mechanic_token_headers)
    assert fail_res.status_code == 200
    fail_data = fail_res.json()["data"]
    assert fail_data["passed"] is False
    assert fail_data["points_awarded"] == 0

    # 2. Submit passing quiz (MOD-01 correct answers: [1, 0, 1])
    pass_res = await client.post("/api/saathi/learning/modules/mod-tread-wear/quiz", json={
        "answers": [1, 0, 1]
    }, headers=mechanic_token_headers)
    assert pass_res.status_code == 200
    pass_data = pass_res.json()["data"]
    assert pass_data["passed"] is True
    assert pass_data["score_percent"] == 100.0
    assert pass_data["points_awarded"] == 50
    assert pass_data["total_points"] >= 50
    assert "BADGE_LEARNING_PIONEER" in pass_data["newly_earned_badges"]

    # 3. Idempotent check: Retaking the quiz with same or higher score must NOT award duplicate points
    retake_res = await client.post("/api/saathi/learning/modules/mod-tread-wear/quiz", json={
        "answers": [1, 0, 1]
    }, headers=mechanic_token_headers)
    assert retake_res.status_code == 200
    retake_data = retake_res.json()["data"]
    assert retake_data["points_awarded"] == 0  # No duplicate points!
    assert retake_data["total_points"] == pass_data["total_points"]  # Total points unchanged


@pytest.mark.asyncio
async def test_customer_referral_workflow_and_isolation(client: AsyncClient, mechanic_token_headers, mechanic_b_headers):
    """Test consent-aware customer follow-up creation, status updates, and mechanic isolation."""
    no_consent_res = await client.post("/api/saathi/referrals", json={
        "customer_name_masked": "Test",
        "vehicle_model": "Test vehicle",
        "tyre_need": "PRESSURE_CHECK",
        "consent_confirmed": False,
    }, headers=mechanic_token_headers)
    assert no_consent_res.status_code == 400

    # 1. Mechanic A logs a referral
    create_res = await client.post("/api/saathi/referrals", json={
        "customer_name_masked": "Ramesh K.",
        "customer_phone_masked": "+91 98*** **123",
        "vehicle_model": "Hero Splendor Plus",
        "tyre_need": "TREAD_WEAR_MONITORING",
        "notes": "Tread depth currently at 2.1mm. Scheduled monsoon checkup.",
        "consent_confirmed": True
    }, headers=mechanic_token_headers)
    assert create_res.status_code == 200
    ref_data = create_res.json()["data"]
    ref_id = ref_data["id"]
    assert ref_data["status"] == "PENDING"
    assert ref_data["customer_name_masked"] == "Ramesh K."

    # 2. Mechanic A updates status to CONTACTED then SERVICE_COMPLETED
    patch_res = await client.patch(f"/api/saathi/referrals/{ref_id}", json={
        "status": "SERVICE_COMPLETED",
        "notes": "Customer visited workshop; fitted new OEM tyre."
    }, headers=mechanic_token_headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "SERVICE_COMPLETED"

    # 3. Mechanic B attempts to access or modify Mechanic A's referral -> must fail (isolation)
    b_patch = await client.patch(f"/api/saathi/referrals/{ref_id}", json={
        "status": "EXPIRED"
    }, headers=mechanic_b_headers)
    assert b_patch.status_code == 404

    # 4. Mechanic B lists referrals -> must NOT see Mechanic A's referral
    b_list = await client.get("/api/saathi/referrals", headers=mechanic_b_headers)
    assert b_list.status_code == 200
    assert len(b_list.json()["data"]["referrals"]) == 0


@pytest.mark.asyncio
async def test_role_authorization_enforcement(client: AsyncClient, rider_token_headers):
    """Test that non-mechanic users (RIDER) cannot access Saathi endpoints (403 Forbidden)."""
    res1 = await client.get("/api/saathi/dashboard", headers=rider_token_headers)
    assert res1.status_code == 403
    assert res1.json()["detail"]["code"] == "FORBIDDEN"

    res2 = await client.get("/api/saathi/learning/modules", headers=rider_token_headers)
    assert res2.status_code == 403

    res3 = await client.post("/api/saathi/referrals", json={
        "customer_name_masked": "Test",
        "vehicle_model": "Honda Activa",
        "tyre_need": "PRESSURE_CHECK"
    }, headers=rider_token_headers)
    assert res3.status_code == 403


@pytest.mark.asyncio
async def test_partner_programmes_disabled_by_default(client: AsyncClient, mechanic_token_headers):
    """Optional partner concepts are absent unless explicitly enabled."""
    settings.ENABLE_PARTNER_PROGRAMMES = False
    res = await client.get("/api/saathi/initiatives", headers=mechanic_token_headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["initiatives"] == []
    assert "disabled" in data["program_disclaimer"].lower()


@pytest.mark.asyncio
async def test_partner_programmes_endpoint_when_enabled(client: AsyncClient, mechanic_token_headers, monkeypatch):
    """Explicit configuration enables proposal-only concepts without implying a partnership."""
    monkeypatch.setattr(settings, "ENABLE_PARTNER_PROGRAMMES", True)
    res = await client.get("/api/saathi/initiatives", headers=mechanic_token_headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["case_study"] == "Optional partner programme concepts"
    assert "No manufacturer partnership" in data["program_disclaimer"]
    initiatives = data["initiatives"]
    assert len(initiatives) >= 4
    categories = [i["category"] for i in initiatives]
    assert "TOOL_SUPPORT" in categories
    assert "SAFETY_SIGNAGE" in categories
    assert "LEARNING_SESSION" in categories
    assert all("case_study_source" not in initiative["tool_specs"] for initiative in initiatives)
