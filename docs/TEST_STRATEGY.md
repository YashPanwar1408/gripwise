# GripWise — Test Strategy

**Status:** PLANNED — not yet implemented
**Date:** 2026-10-10

---

## 1. Principles

1. **Tests are the first proof of claims.** Every acceptance criterion in PRODUCT_REQUIREMENTS.md maps to at least one automated test.
2. **Mock provider must always be tested.** The real CV pipeline is optional; the mock is never optional.
3. **Safety-critical labels are tested.** The absence of "safe"/"unsafe" verdicts, the presence of confidence tiers, and the presence of caveat text are asserted in tests.
4. **No test exercises real model weights in CI.** CI runs against mock provider only; real CV tests are gated with `@pytest.mark.real_cv` and skipped unless `GRIPWISE_TEST_REAL_CV=true`.
5. **AI module unit tests use synthetic inputs.** Consistent with BharatDrive's approach and the tyreHealth fallback pattern. Synthetic test inputs are clearly labelled as synthetic.
6. **Test coverage targets:** Backend 80% line coverage minimum. Frontend critical paths (auth, upload flow, inspection result) have Playwright E2E coverage.

---

## 2. Test Layers

```
┌──────────────────────────────────────────────────┐
│  E2E Tests (Playwright)                           │
│  Full browser flows: register → upload → result   │
│  Mechanic consent → finding → service record      │
│  Reminder display and dismissal                   │
└──────────────────┬───────────────────────────────┘
                   │ exercises
┌──────────────────▼───────────────────────────────┐
│  Integration Tests (pytest + httpx AsyncClient)   │
│  FastAPI route handlers + real DB (test schema)   │
│  InferenceProvider → MockProvider → DB → response │
└──────────────────┬───────────────────────────────┘
                   │ exercises
┌──────────────────▼───────────────────────────────┐
│  Unit Tests (pytest / Jest)                       │
│  Individual functions and classes                 │
│  AI sub-modules, services, schemas, utilities     │
└──────────────────────────────────────────────────┘
```

---

## 3. Backend Tests (pytest)

### 3.1 Test Infrastructure

```python
# conftest.py (planned)
@pytest.fixture
async def db():
    # Creates a test schema; drops after test
    # Uses PostgreSQL test instance from docker-compose.test.yml
    ...

@pytest.fixture
async def client(db):
    # httpx.AsyncClient against FastAPI app
    ...

@pytest.fixture
def rider_token(client):
    # Registers a test rider, returns JWT
    ...

@pytest.fixture
def mechanic_token(client):
    # Registers a test mechanic, returns JWT
    ...
```

### 3.2 Auth Tests

| Test | Assertion |
|---|---|
| `test_register_rider_success` | 201, returns access_token and refresh_token |
| `test_register_mechanic_requires_workshop_name` | 422 if workshop_name missing |
| `test_login_correct_credentials` | 200, returns tokens |
| `test_login_wrong_password` | 401 |
| `test_refresh_valid_token` | 200, new access_token |
| `test_refresh_expired_token` | 401 |
| `test_protected_endpoint_without_token` | 401 |
| `test_rider_cannot_access_admin_endpoint` | 403 |

### 3.3 Vehicle and Tyre Tests

| Test | Assertion |
|---|---|
| `test_create_vehicle_success` | 201, vehicle in DB |
| `test_list_vehicles_only_own` | Rider cannot see other riders' vehicles |
| `test_create_tyre_position_valid_positions` | All valid position enums accepted |
| `test_create_duplicate_tyre_position` | 422 or 409 |

### 3.4 Inspection Tests (Mock Provider)

| Test | Assertion |
|---|---|
| `test_submit_inspection_jpeg` | 202 returned; inspection_id in DB |
| `test_submit_inspection_png` | 202 returned |
| `test_submit_inspection_too_large` | 413 IMAGE_TOO_LARGE |
| `test_submit_inspection_wrong_type` | 415 IMAGE_INVALID_TYPE |
| `test_submit_inspection_other_riders_tyre` | 404 NOT_FOUND |
| `test_poll_inspection_complete` | status=COMPLETE, observations non-empty |
| `test_poll_inspection_has_confidence_tiers` | Every observation has confidence field |
| `test_poll_inspection_has_caveat_on_tread_score` | tread_score observation has non-null caveat |
| `test_poll_inspection_no_safe_unsafe_verdict` | "safe" not in any response field value |
| `test_poll_inspection_provider_labelled` | inference_provider = "mock" |
| `test_poll_inspection_model_version_present` | model_version not null or empty |
| `test_image_served_authenticated` | 200 with auth token |
| `test_image_not_served_unauthenticated` | 401 |
| `test_audit_event_on_inspection_create` | audit_events row exists |

### 3.5 Mechanic Tests

| Test | Assertion |
|---|---|
| `test_mechanic_cannot_access_inspection_without_consent` | 403 FORBIDDEN |
| `test_rider_grants_consent_mechanic_can_access` | 200 after consent |
| `test_rider_revokes_consent_mechanic_blocked` | 403 after revoke |
| `test_mechanic_records_finding_verified` | finding in DB with verified=true |
| `test_mechanic_records_finding_unverified` | finding in DB with verified=false |
| `test_mechanic_records_service_record` | service_records row exists |
| `test_rider_sees_mechanic_verified_badge` | GET /inspections/{id} shows mechanic_findings |
| `test_ai_and_mechanic_fields_distinct` | observations from AI, mechanic_findings from mechanic; no mixing |

### 3.6 Reminder Tests

| Test | Assertion |
|---|---|
| `test_reminder_triggered_on_low_tread_score` | reminder_rules evaluated post-inspection; reminder created |
| `test_reminder_shows_rule_name_and_description` | GET /reminders returns rule_description |
| `test_reminder_dismissed_with_reason` | PATCH sets status=DISMISSED, dismissed_reason saved |
| `test_reminder_actioned` | PATCH sets status=ACTIONED |

### 3.7 AI Module Unit Tests

```python
# gripwise/ai/tests/ (planned)

class TestMockProvider:
    def test_returns_inference_result(self):
        result = MockProvider().analyse(b"<any bytes>")
        assert isinstance(result, InferenceResult)

    def test_provider_is_labelled_mock(self):
        result = MockProvider().analyse(b"<any bytes>")
        assert result.provider == "mock"

    def test_every_observation_has_confidence_tier(self):
        result = MockProvider().analyse(b"<any bytes>")
        for obs in result.observations:
            assert obs.confidence in [t.value for t in ConfidenceTier]

    def test_tread_score_has_caveat(self):
        result = MockProvider().analyse(b"<any bytes>")
        tread = next(o for o in result.observations if o.field == "tread_score")
        assert tread.caveat is not None and len(tread.caveat) > 10

    def test_no_safe_unsafe_in_observations(self):
        result = MockProvider().analyse(b"<any bytes>")
        all_text = str(result)
        assert "is safe" not in all_text.lower()
        assert "is unsafe" not in all_text.lower()

    def test_quality_fail_path(self):
        result = MockProvider(quality_scenario="fail").analyse(b"<blur>")
        assert result.image_quality == "FAIL"
        assert result.recommended_action == "analysis_failed"

class TestQualityChecker:
    def test_sharp_bright_image_passes(self):
        img = _make_sharp_image()
        result = QualityChecker().check(img)
        assert result.status == "PASS"

    def test_blurred_image_fails(self):
        img = _make_blurred_image()
        result = QualityChecker().check(img)
        assert "BLUR_DETECTED" in result.issues

    def test_dark_image_fails(self):
        img = _make_dark_image()
        result = QualityChecker().check(img)
        assert "LOW_BRIGHTNESS" in result.issues

class TestTreadAnalyser:
    def test_returns_score_between_0_and_100(self):
        roi = _make_synthetic_tyre_roi()
        score = TreadAnalyser().analyse(roi)
        assert 0 <= score.value <= 100

    def test_score_is_relative_indicator_not_depth(self):
        # Caveat must mention it is not a depth measurement
        roi = _make_synthetic_tyre_roi()
        score = TreadAnalyser().analyse(roi)
        assert "depth" in score.caveat.lower() or "mm" in score.caveat.lower()

    def test_error_returns_not_available_not_50(self):
        score = TreadAnalyser().analyse(None)
        assert score.confidence == ConfidenceTier.NOT_AVAILABLE

# @pytest.mark.real_cv tests (skipped in CI unless GRIPWISE_TEST_REAL_CV=true)
class TestCVProviderRealImage:
    @pytest.mark.real_cv
    def test_real_tyre_image_returns_tread_score(self):
        with open("tests/fixtures/tyre_clear.jpg", "rb") as f:
            result = CVProvider().analyse(f.read())
        tread = next(o for o in result.observations if o.field == "tread_score")
        assert tread.confidence in (ConfidenceTier.HIGH, ConfidenceTier.MEDIUM)
```

### 3.8 Analytics Tests

| Test | Assertion |
|---|---|
| `test_analytics_overview_accessible_to_admin` | 200 for ADMIN role |
| `test_analytics_overview_forbidden_to_rider` | 403 for RIDER role |
| `test_analytics_no_pii_in_response` | No email, mobile, or name fields in response body |

---

## 4. Frontend Tests

### 4.1 Unit Tests (Jest + React Testing Library)

| Component | What is tested |
|---|---|
| `ConfidencePill` | Renders correct label and colour for each ConfidenceTier value |
| `ObservationCard` | Shows field name, value, confidence, explanation, and caveat |
| `UncertaintyBanner` | Appears when any observation has LOW_CONFIDENCE or NOT_AVAILABLE |
| `VerifiedBadge` | Shows "AI Analysis" vs "Mechanic Verified" correctly |
| `InspectionReport` | Does not render "safe" or "unsafe" as a verdict anywhere |
| `ProviderBadge` | Shows "Mock Analysis" when provider="mock" |

### 4.2 E2E Tests (Playwright)

| Flow | Steps | Key Assertions |
|---|---|---|
| Rider registration | Navigate to /register → fill form → submit | Lands on dashboard; no errors |
| Full inspection flow | Login → add vehicle → add tyre → upload JPEG → poll result | Result page shows observations with confidence tiers; caveat text visible; no safe/unsafe verdict |
| Quality failure guidance | Upload blurred image | Quality tips shown; specific issue identified; re-upload CTA present |
| Mock provider labelling | Complete any inspection | "Mock Analysis" badge visible on result page |
| Mechanic consent flow | Rider grants access → mechanic logs in → views inspection → records finding | Finding appears in rider's inspection history with Mechanic Verified label |
| Reminder display | Inject low tread inspection → check rider dashboard | Reminder card shows rule description and urgency colour |
| Reminder dismissal | Click Dismiss → enter reason → confirm | Reminder removed from list; reason saved |
| Road safety disclaimer | Enable road safety flag → navigate to ride tab | Disclaimer text visible before any monitoring data |

---

## 5. Database Migration Tests

| Test | What is verified |
|---|---|
| `test_migrations_up` | `alembic upgrade head` completes without error |
| `test_migrations_down` | `alembic downgrade base` completes without error |
| `test_migrations_idempotent` | Running upgrade head twice does not error |

---

## 6. CI Configuration (Planned)

```yaml
# .github/workflows/ci.yml (planned)
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test }
    steps:
      - checkout
      - setup Python 3.11
      - pip install -r backend/requirements-dev.txt
      - alembic upgrade head
      - pytest backend/tests/ --cov=backend --cov-fail-under=80
      - GRIPWISE_TEST_REAL_CV=false pytest ai/tests/ --cov=ai --cov-fail-under=80

  frontend:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup Node 20
      - npm ci
      - npm test -- --coverage
      - npx playwright install --with-deps
      - npx playwright test  # runs against mock backend
```

---

## 7. Acceptance Criteria Traceability

| AC from PRD | Test(s) |
|---|---|
| AC-1: Rider flow works end-to-end | Playwright: Full inspection flow |
| AC-2: Confidence tiers and uncertainty labels on all AI outputs | `test_poll_inspection_has_confidence_tiers`, `test_poll_inspection_has_caveat_on_tread_score`, `ObservationCard` Jest test |
| AC-3: System runs with mock provider — no crashes | `test_poll_inspection_complete` (mock default in CI) |
| AC-4: Mechanic can record physical finding | `test_mechanic_records_finding_verified`, Playwright mechanic consent flow |
| AC-5: AI and mechanic findings visually distinct | `test_ai_and_mechanic_fields_distinct`, `VerifiedBadge` Jest test |
| AC-6: Audit log records inspection events | `test_audit_event_on_inspection_create` |
| AC-7: Guidance rules visible to rider | Playwright: Reminder display; `test_reminder_shows_rule_name_and_description` |
| AC-8: No "safe"/"unsafe" verdict | `test_poll_inspection_no_safe_unsafe_verdict`, `test_no_safe_unsafe_in_observations`, `InspectionReport` Jest test |

---

## 8. What Is Not Tested Automatically

| Item | Reason | Manual Check |
|---|---|---|
| Real-world tyre detection accuracy | No labelled tyre dataset in repo | Manual review with held-out images when available |
| Tread score calibration vs actual mm depth | No physical measurement data | Deferred to post-hackathon validation |
| Driver monitoring single-subject limitations | Requires human subject | Disclosed in UI; not automatable |
| Mobile device camera quality in the field | Requires physical device | Manual device testing |
| Ultralytics AGPL-3.0 compliance in distribution | Legal question | Legal review |
