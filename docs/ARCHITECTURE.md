# GripWise — Architecture

**Status:** PLANNED — not yet implemented
**Date:** 2026-10-10

---

## 1. System Overview

```
                        ┌──────────────────────────────────────────────┐
                        │              RIDER / MECHANIC BROWSER          │
                        │         Next.js 14  (TypeScript + Tailwind)    │
                        │  Rider Workspace │ Mechanic Workspace │ Admin  │
                        └───────────────────────┬──────────────────────┘
                                                │ HTTPS / REST+JSON
                                                ▼
                        ┌──────────────────────────────────────────────┐
                        │             FastAPI Backend (Python)           │
                        │                                                │
                        │  /api/auth      /api/vehicles  /api/inspections│
                        │  /api/mechanic  /api/reminders /api/analytics  │
                        │                    │                           │
                        │        ┌───────────┴──────────┐               │
                        │        │   AI Service Layer    │               │
                        │        │  (gripwise/ai/)       │               │
                        │        │                       │               │
                        │        │  InferenceProvider    │               │
                        │        │  (Protocol/ABC)       │               │
                        │        │       ┌───────┴────┐  │               │
                        │        │  MockProvider  CVProvider │           │
                        │        │  (always on)  (real CV)  │           │
                        │        └──────────────────────┘               │
                        │                    │                           │
                        └────────────────────┼───────────────────────── ┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                         │
                    ▼                        ▼                         ▼
           ┌──────────────┐       ┌──────────────────┐     ┌──────────────────┐
           │  PostgreSQL  │       │  Local Filesystem │     │  structlog       │
           │  (primary DB)│       │  (image store)    │     │  (JSON logs)     │
           └──────────────┘       └──────────────────┘     └──────────────────┘
```

---

## 2. Layer Responsibilities

### 2.1 Frontend — Next.js 14

| Responsibility | Notes |
|---|---|
| Rider and Mechanic UX | App Router, TypeScript, Tailwind CSS |
| Server-Side Rendering | Inspection history, dashboard pages pre-rendered |
| Client-Side Interactivity | Image upload, live analysis status polling |
| Authentication | NextAuth.js with JWT; roles: RIDER, MECHANIC, ADMIN |
| API Client | Type-safe fetch wrapper generated from OpenAPI schema |
| i18n | English MVP; Hindi/Marathi string files added (initially empty) |
| Testing | Jest (unit), Playwright (E2E) |

**Component structure (planned):**
```
frontend/
├── app/
│   ├── (auth)/           login, register
│   ├── (rider)/          dashboard, vehicles, inspections, history
│   ├── (mechanic)/       queue, inspection-detail, service-record
│   └── (admin)/          analytics, audit-log
├── components/
│   ├── ui/               Button, Card, Badge, Gauge, ConfidencePill
│   ├── inspection/       InspectionReport, ObservationCard, UncertaintyBanner
│   └── mechanic/         FindingForm, ServiceRecordForm, VerifiedBadge
└── lib/
    ├── api.ts            typed fetch client
    └── types.ts          shared TypeScript types (generated from OpenAPI)
```

### 2.2 Backend — FastAPI

| Responsibility | Notes |
|---|---|
| REST API | JSON over HTTPS; OpenAPI spec auto-generated |
| Business logic | Services layer; no business logic in route handlers |
| Authentication | JWT validation middleware; role-based access |
| Image handling | Multipart upload, validation, storage, hash computation |
| AI orchestration | Calls InferenceProvider; never calls CV directly from routes |
| Database access | SQLAlchemy 2.0 async ORM |
| Migrations | Alembic |
| Background tasks | FastAPI BackgroundTasks (MVP); Celery if async inference needed |
| Structured logging | structlog with JSON output |

**Package structure (planned):**
```
backend/
├── api/
│   ├── auth.py           /api/auth/*
│   ├── vehicles.py       /api/vehicles/*
│   ├── inspections.py    /api/inspections/*
│   ├── mechanic.py       /api/mechanic/*
│   ├── reminders.py      /api/reminders/*
│   └── analytics.py      /api/analytics/*
├── services/
│   ├── inspection_service.py
│   ├── ai_service.py       (delegates to ai/ layer)
│   ├── reminder_service.py
│   └── audit_service.py
├── models/               (SQLAlchemy ORM)
├── schemas/              (Pydantic v2 request/response)
├── middleware/           (auth, logging, error handling)
└── migrations/           (Alembic)
```

### 2.3 AI Inference Layer — gripwise/ai/

This is the critical isolation boundary. The backend calls `InferenceProvider.analyse(image_bytes)` and never directly imports OpenCV, ultralytics, or TensorFlow.

```python
# gripwise/ai/interfaces.py (planned)

from typing import Protocol
from dataclasses import dataclass

class ConfidenceTier(str, Enum):
    HIGH = "HIGH_CONFIDENCE"
    MEDIUM = "MEDIUM_CONFIDENCE"
    LOW = "LOW_CONFIDENCE"
    NOT_AVAILABLE = "NOT_AVAILABLE"

@dataclass
class TyreObservation:
    field: str
    value: object
    confidence: ConfidenceTier
    explanation: str
    caveat: str | None = None

@dataclass
class InferenceResult:
    provider: str           # "mock" | "cv_pipeline"
    model_version: str
    image_quality: str      # "PASS" | "FAIL" | "DEGRADED"
    quality_issues: list[str]
    detected_tyres: int
    recommended_action: str
    observations: list[TyreObservation]
    raw_scores: dict
    inference_ms: float

class InferenceProvider(Protocol):
    def analyse(self, image_bytes: bytes) -> InferenceResult: ...
    def health_check(self) -> dict: ...
```

**Provider selection:**
```
GRIPWISE_INFERENCE_PROVIDER env var:
  "mock"        -> MockProvider (default, always available)
  "cv_pipeline" -> CVProvider (requires OpenCV + model weights)
```

**Mock provider guarantees:**
- Always returns a deterministic result for any input
- Exercises all downstream code paths (quality pass, quality fail, high confidence, low confidence)
- Clearly labelled in all outputs: `"provider": "mock"`

**CVProvider (planned):**
- Adapted from tyreHealth-main detection + tread analysis logic
- Outputs wrapped in `TyreObservation` with explicit confidence tiers
- Requires: `opencv-python`, `ultralytics`, `scikit-learn`, `joblib`
- Loads models lazily; reports NOT_AVAILABLE per-observation if model is missing

### 2.4 Database — PostgreSQL

See DATA_MODEL.md for full schema. Key tables:
- `users` (riders + mechanics + admins)
- `vehicles`
- `tyre_positions`
- `inspections`
- `inspection_observations` (AI outputs, one row per observation field)
- `mechanic_findings` (physical verification by mechanic)
- `service_records`
- `maintenance_reminders`
- `reminder_rules`
- `audit_events`
- `consent_records`
- `analytics_events`

### 2.5 File Storage

MVP: local filesystem under `GRIPWISE_IMAGE_DIR` (configurable).
Interface: `ImageStore` with `store(image_bytes, filename) -> path` and `retrieve(path) -> bytes`.
S3-compatible implementation planned for production.
Images are content-addressed (SHA-256 hash = filename). Duplicate uploads deduplicated.

---

## 3. Deployment Architecture (Local Development)

```
docker-compose.yml services:
  db          PostgreSQL 16 (port 5432)
  backend     FastAPI (port 8000, hot-reload)
  frontend    Next.js dev server (port 3000, hot-reload)
  pgadmin     (optional, port 5050)
```

Environment:
- `.env.local` for frontend (NEXTAUTH_SECRET, NEXT_PUBLIC_API_URL)
- `.env` for backend (DATABASE_URL, GRIPWISE_INFERENCE_PROVIDER, IMAGE_DIR, JWT_SECRET)

Single command to start: `make dev` (runs `docker-compose up --build`)

---

## 4. Security Architecture

| Control | Implementation |
|---|---|
| Authentication | JWT (HS256), 24h access token, 7d refresh token |
| Authorisation | Role-based (RIDER/MECHANIC/ADMIN), enforced in FastAPI middleware |
| Image access | Images served through authenticated API endpoint, not directly from filesystem |
| Data isolation | Riders can only see their own data; mechanic access requires explicit rider consent |
| Input validation | Pydantic v2 strict mode on all request schemas |
| SQL injection | SQLAlchemy ORM parameterised queries only; raw SQL banned |
| File uploads | MIME type check, max size (10 MB), virus scan placeholder |
| Secrets | Never in source code; loaded from environment variables only |
| Consent | Consent records stored per inspection; mechanic access requires active consent |
| HTTPS | Enforced in production; local dev HTTP acceptable |

---

## 5. AI Module Boundary — Critical Design Rules

These rules exist because the reference audit found misleading confidence signals:

1. **No raw percentage as tread depth.** Tread score 0-100 is a "relative wear indicator". The UI must display this caveat.
2. **No binary safe/unsafe.** Recommended action uses an enum with explicit uncertainty tiers.
3. **No hardcoded confidence.** CVProvider never hardcodes confidence=0.86; it derives confidence from image quality and model type.
4. **Mock is the default.** Real CV pipeline is opt-in. Mock is always exercised in CI.
5. **Provider label in every response.** Frontend always displays provider type so a human knows whether they are seeing real or mock analysis.
6. **Model version in every record.** Stored in the database so future model updates don't silently change the meaning of historical records.

---

## 6. Optional Road Safety Module — Integration Design

Source: BharatDrive-x-Twin-main `driver_monitoring/`, `fusion/`, `alerts/`, `road_perception/`

When feature flag `GRIPWISE_ROAD_SAFETY=true`:

```
RideSafetySession:
  ├── DriverMonitor (adapted BharatDrive driver_monitoring/)
  │     EAR → blink → PERCLOS → reliability → readiness → state machine
  ├── RoadDetector (BharatDrive road_perception/ MockDetector in MVP)
  │     Scenario JSON playback → hazard list → complexity index
  ├── RideSafetyFusion (adapted BharatDrive fusion/journey_safety.py)
  │     driver readiness × road complexity × tyre risk → RideSafetyScore
  └── AlertManager (BharatDrive alerts/ + new tyre message keys)
```

**Tyre risk integration:** RideSafetyFusion receives `tyre_risk_factor` (0.0–1.0) derived from the most recent tyre inspection. A heavily worn tyre on a wet road at high speed increases the composite risk.

**UI disclaimer (mandatory):**
> "Ride Safety monitoring is a research prototype. Single-subject calibration. Not validated for your device, lighting, or road conditions. Do not rely on this for safety decisions. Always follow traffic laws and consult a mechanic for tyre concerns."

---

## 7. User Journey Diagrams

### 7.1 Rider — First Inspection

```
Rider → Register → Add Vehicle → Add Tyre Position
  → Upload Image → Quality Check
       FAIL → "Image tips" page → Re-upload
       PASS → Analysis queued → Result page
                 → Observations (each with confidence tier)
                 → Recommended action
                 → "Get mechanic review" CTA
                 → Save to history
```

### 7.2 Mechanic — Review and Verify

```
Rider shares inspection → Mechanic receives notification
  → Mechanic views AI report
  → For each observation → Record physical finding (or "Unable to verify")
  → Record service actions
  → Mark complete → Rider sees "Mechanic Verified" badge on inspection
```

### 7.3 Maintenance Reminder Trigger

```
Rule engine runs (daily cron / post-inspection)
  → Evaluates reminder_rules against rider inspection history
  → Generates reminder if threshold crossed
  → Rider receives in-app notification
  → Rider views reminder with rule explanation
  → Rider: Dismiss (with reason) | Schedule mechanic | Mark done
```
