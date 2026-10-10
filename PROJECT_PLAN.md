# GripWise — Project Plan

**Status:** PLANNED — not yet implemented
**Date:** 2026-10-10
**Version:** 0.1 (pre-implementation)

---

## 1. What GripWise Is

GripWise is an AI-assisted tyre-safety and rider-trust platform designed for the Indian two-wheeler market. It connects riders, mechanics, and tyre-care intelligence in a single verifiable, explainable, offline-capable system.

GripWise addresses two hackathon challenge narratives simultaneously:

- **Tata Imagination Challenge:** Improve access to tyre-safety awareness, preventive maintenance, and explainable safety guidance for Indian riders who currently have no objective way to assess tyre health.
- **Eurogrip TORQ Challenge 4.0:** Build rider trust, mechanic engagement, tyre-care awareness, repeat customer engagement, and measurable brand preference. GripWise does NOT claim any partnership or endorsement from Eurogrip or any organisation.

---

## 2. What GripWise Is Not

- GripWise is not a medical device, automotive certification system, or safety guarantee.
- GripWise does not replace a trained mechanic's professional judgement.
- GripWise does not claim its AI outputs are ground truth — every inference is explicitly labelled with its provenance and confidence tier.
- GripWise does not require cloud GPUs, paid APIs, or internet connectivity for core analysis.

---

## 3. Core Product Modules

| Module | Purpose | Status |
|---|---|---|
| M1 — Rider Workspace | Vehicle registration, image submission, inspection history, maintenance guidance | PLANNED |
| M2 — Tyre Intelligence | Image quality validation, CV analysis, explainable observations, uncertainty handling | PLANNED |
| M3 — Mechanic Workspace | Record inspections, document service, distinguish AI vs mechanic findings | PLANNED |
| M4 — Maintenance Intelligence | Reminders, transparent rules, maintenance history | PLANNED |
| M5 — Trust and Audit | Timestamps, model versions, consent, traceability | PLANNED |
| M6 — Road Safety Module (Optional) | Rider fatigue + hazard detection integration | PLANNED (gated) |
| M7 — Engagement Analytics | Inspection completion, repeat usage, mechanic participation | PLANNED |

---

## 4. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | Next.js 14+, TypeScript, Tailwind CSS | Type-safe, component-driven, SSR/SSG capable |
| Backend API | Python FastAPI | Native Python AI integration, async, OpenAPI auto-docs |
| Database | PostgreSQL 16 | Relational integrity for audit trail; JSONB for flexible inference payloads |
| AI Inference | Isolated Python modules (gripwise/ai/) | Stable interfaces; swappable mock/real providers |
| Authentication | NextAuth.js (JWT) | Session management without external auth service |
| File Storage | Local filesystem (MVP); S3-compatible interface | Tyre image storage; local-first |
| Migrations | Alembic (Python) | Versioned schema migrations |
| Testing | pytest (backend), Jest + Playwright (frontend) | Automated at unit and E2E level |
| Logging | structlog (Python) | Structured JSON logs |
| Local Dev | Docker Compose | Single-command local environment |

---

## 5. Repository Structure (Planned)

```
gripwise/
├── docs/                          (audit + design docs — current)
├── frontend/                      (Next.js app)
│   ├── app/                       (App Router pages)
│   ├── components/                (shared UI components)
│   ├── lib/                       (API clients, types)
│   └── tests/                     (Jest unit + Playwright E2E)
├── backend/                       (FastAPI application)
│   ├── api/                       (route handlers)
│   ├── services/                  (business logic)
│   ├── models/                    (SQLAlchemy ORM models)
│   ├── schemas/                   (Pydantic request/response schemas)
│   ├── migrations/                (Alembic)
│   └── tests/                     (pytest)
├── ai/                            (inference modules)
│   ├── interfaces.py              (Abstract protocols — stable contract)
│   ├── providers/
│   │   ├── mock_provider.py       (deterministic mock — always available)
│   │   └── cv_provider.py         (real OpenCV/YOLO pipeline)
│   └── tyre_pipeline/             (adapted from tyreHealth-main)
├── docker-compose.yml
├── Makefile
├── PROJECT_PLAN.md                (this file)
└── refrences/                     (read-only, never modified)
```

---

## 6. Development Phases

| Phase | Name | Goal | Target |
|---|---|---|---|
| 0 | Foundation | Repo scaffold, Docker, CI, DB migrations, auth skeleton | Sprint 1 |
| 1 | Rider MVP | Image upload, mock analysis, history view, audit log | Sprint 2–3 |
| 2 | AI Integration | Real CV pipeline behind interface, quality gating, uncertainty labels | Sprint 4–5 |
| 3 | Mechanic Module | Mechanic workspace, verified findings, service history | Sprint 6 |
| 4 | Trust Layer | Full audit trail, consent management, version tracking | Sprint 7 |
| 5 | Road Safety Module | BharatDrive driver-monitoring integration (gated feature flag) | Sprint 8 |
| 6 | Analytics | Engagement metrics, mechanic participation, repeat usage | Sprint 9 |
| 7 | Polish & Demo | Performance, accessibility, demo data, presentation | Sprint 10 |

---

## 7. Unresolved Questions (Require Decisions)

| # | Question | Impact | Owner |
|---|---|---|---|
| Q1 | Is Eurogrip a competition judge or potential partner? If partner, does this change data sharing requirements? | Branding, data sharing | Product |
| Q2 | Do we target motorcycle only, or all two-wheelers (scooters, e-bikes)? | Image model scope | AI |
| Q3 | What is the image capture UX — upload, QR-to-camera, or embedded camera in PWA? | Frontend architecture | Frontend |
| Q4 | Do mechanics use the same web app or a separate PWA/native app? | Routing, auth roles | Full Stack |
| Q5 | Is offline-first for mechanics required (no connectivity in rural workshops)? | PWA requirements, sync strategy | Full Stack |
| Q6 | What labelled tyre image dataset will be used for retraining the CNN? | AI timeline | AI |
| Q7 | Are we targeting Hindi/Marathi localisation at hackathon scope or deferred? | Frontend i18n | Frontend |
| Q8 | Ultralytics AGPL-3.0 licence — will GripWise be open-sourced? | Licence strategy | Product/Legal |

---

## 8. Non-Negotiable Constraints

1. Every AI inference output carries an explicit confidence tier and uncertainty label.
2. Mock provider is always available so the app runs without real model weights.
3. Mechanic-verified findings are stored separately from AI observations and clearly distinguished in the UI.
4. No raw video is stored without explicit consent.
5. All recommendation rules are visible and auditable — no black-box guidance.
6. The reference repositories in gripwise/refrences/ are never modified.
