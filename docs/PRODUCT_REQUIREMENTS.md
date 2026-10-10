# GripWise — Product Requirements

**Status:** PLANNED — not yet implemented
**Date:** 2026-10-10
**Version:** 0.1

All features below are PLANNED unless explicitly marked otherwise.

---

## 1. Product Goals

### 1.1 Primary Goals

| Goal | Measurable Outcome |
|---|---|
| Tyre safety awareness | A rider can submit a tyre image and receive explainable, honest observations within 30 seconds |
| Preventive maintenance | Riders with inspection history receive relevant, rule-based maintenance reminders |
| Mechanic engagement | Mechanics can record verified findings and build a traceable service history |
| Rider trust | Every AI output is labelled with confidence and uncertainty; no unsupported guarantees |
| Brand engagement (TORQ) | Repeat inspection usage and mechanic participation are measurable and improving |

### 1.2 Anti-Goals

- GripWise does NOT replace a physical tyre inspection by a trained mechanic.
- GripWise does NOT guarantee safety from any specific tyre defect.
- GripWise does NOT claim partnerships with Eurogrip or any commercial organisation.
- GripWise does NOT store raw images longer than necessary without explicit user consent.

---

## 2. User Personas

### P1 — Rider (Primary)
**Profile:** Indian two-wheeler rider, 20–45 years old, varying technical literacy.
**Goals:** Understand if tyres are safe, know when to service them, trust the app's guidance.
**Pain points:** No objective way to assess tyre health; distrust of mechanic recommendations; cost anxiety.
**Key journeys:** Register vehicle → submit tyre image → read observations → follow maintenance guidance.

### P2 — Mechanic (Secondary)
**Profile:** Roadside or workshop mechanic, may have limited smartphone literacy.
**Goals:** Record service work, build credibility with customers, access inspection history.
**Pain points:** No digital record-keeping; customers distrust verbal reports.
**Key journeys:** View rider's AI inspection → record physical findings → mark service completed.

### P3 — Administrator / Analyst (Internal)
**Profile:** GripWise operator or hackathon evaluator.
**Goals:** Monitor system health, inspect audit logs, understand engagement metrics.
**Key journeys:** View analytics dashboard → inspect inspection records → check audit trail.

---

## 3. Module Requirements

### M1 — Rider Workspace

#### M1.1 Vehicle Registration
- REQ-R01: Rider can create an account with mobile number or email [PLANNED]
- REQ-R02: Rider can register one or more vehicles (make, model, year, registration) [PLANNED]
- REQ-R03: Rider can register each tyre position (front/rear, left/right) per vehicle [PLANNED]
- REQ-R04: Rider can view and edit registered vehicles [PLANNED]

#### M1.2 Tyre Image Submission
- REQ-R05: Rider can submit a tyre image (JPEG/PNG/WEBP, max 10 MB) per tyre position [PLANNED]
- REQ-R06: System validates image quality before analysis (blur, brightness, tyre visibility) [PLANNED]
- REQ-R07: System provides clear guidance if image quality is insufficient [PLANNED]
- REQ-R08: Submission includes metadata (tyre position, current odometer reading, date) [PLANNED]

#### M1.3 Inspection History
- REQ-R09: Rider can view all past inspections per vehicle/tyre position in reverse chronological order [PLANNED]
- REQ-R10: Each inspection record shows AI observations, confidence tiers, and mechanic findings [PLANNED]
- REQ-R11: Rider can compare two inspections side-by-side [PLANNED]

#### M1.4 Maintenance Guidance
- REQ-R12: System displays rule-based maintenance guidance based on inspection observations [PLANNED]
- REQ-R13: All guidance rules are visible to the rider ("This recommendation is based on: tread score below 40") [PLANNED]
- REQ-R14: Rider receives push/in-app reminders for scheduled inspections [PLANNED]
- REQ-R15: Guidance never uses language implying safety guarantee ("Your tyre is safe" is prohibited) [PLANNED]

---

### M2 — Tyre Intelligence

#### M2.1 Image Quality Validation
- REQ-T01: System checks image for minimum resolution (min 640px on shortest axis) [PLANNED]
- REQ-T02: System checks for blur (Laplacian variance threshold) [PLANNED]
- REQ-T03: System checks for sufficient brightness [PLANNED]
- REQ-T04: System checks that a tyre is present in the image (detection confidence gate) [PLANNED]
- REQ-T05: Quality failures return a structured error with specific guidance, not a generic error [PLANNED]

#### M2.2 AI Analysis Pipeline
- REQ-T06: System runs tyre detection (YOLOv8 → Hough-circle fallback) [PLANNED]
- REQ-T07: System runs tread wear scoring (OpenCV Canny edge density) [PLANNED]
- REQ-T08: System runs anomaly detection (contour + geometric analysis) [PLANNED]
- REQ-T09: System runs condition classification (CNN — requires real model weights) [PLANNED]
- REQ-T10: A mock inference provider returns deterministic plausible outputs when real models are unavailable [PLANNED]

#### M2.3 Explainability and Uncertainty
- REQ-T11: Every AI output field carries one of: HIGH_CONFIDENCE, MEDIUM_CONFIDENCE, LOW_CONFIDENCE, or NOT_AVAILABLE [PLANNED]
- REQ-T12: Every AI output references the model version and inference provider type (mock/cv_pipeline) [PLANNED]
- REQ-T13: Tread score is labelled "relative wear indicator (not a depth measurement in mm)" [PLANNED]
- REQ-T14: Lifespan estimates (when implemented) are labelled "estimated range, not validated against real-world data" [PLANNED]
- REQ-T15: System never produces a binary "safe/unsafe" verdict — only observations and recommendations [PLANNED]

#### M2.4 Recommended Actions
- REQ-T16: System produces a structured recommended action from: {ok, monitor, inspect_soon, replace_urgently, seek_mechanic_now} [PLANNED]
- REQ-T17: Each recommended action links to the observation(s) that drove it [PLANNED]

---

### M3 — Mechanic Workspace

#### M3.1 Mechanic Account
- REQ-M01: Mechanic can create a professional account with name and workshop details [PLANNED]
- REQ-M02: Rider can invite a mechanic to view their inspection [PLANNED]
- REQ-M03: Mechanic can search for a rider by vehicle registration (with rider consent) [PLANNED]

#### M3.2 Inspection Review and Verification
- REQ-M04: Mechanic can view the AI observations for any inspection they have been granted access to [PLANNED]
- REQ-M05: Mechanic can record their own physical finding for each observation category [PLANNED]
- REQ-M06: Mechanic findings are stored with a distinct provenance label ("MECHANIC_VERIFIED") [PLANNED]
- REQ-M07: UI clearly distinguishes AI observations from mechanic-verified findings at all times [PLANNED]

#### M3.3 Service Recording
- REQ-M08: Mechanic can record service actions (tyre rotation, replacement, inflation adjustment, puncture repair) [PLANNED]
- REQ-M09: Service records are linked to specific tyre positions and inspection IDs [PLANNED]
- REQ-M10: Service records include labour notes (free text, max 500 chars) [PLANNED]
- REQ-M11: Completed service records are visible to the rider in inspection history [PLANNED]

---

### M4 — Maintenance Intelligence

- REQ-MX01: System applies configurable rule set to inspection observations and generates maintenance reminders [PLANNED]
- REQ-MX02: Rules are stored as named, versioned, human-readable records (not embedded business logic) [PLANNED]
- REQ-MX03: Example rules: "If tread score < 35 for two consecutive inspections → recommend inspection within 7 days" [PLANNED]
- REQ-MX04: Reminders include the specific rule and observation that triggered them [PLANNED]
- REQ-MX05: Rider can dismiss a reminder with a reason [PLANNED]
- REQ-MX06: Mileage-based reminders supported (e.g., "inspect every 5,000 km") [PLANNED]

---

### M5 — Trust and Audit

- REQ-A01: Every inspection record includes: created_at (UTC), model_version, provider_type, image_hash [PLANNED]
- REQ-A02: Inspection records are immutable after creation; corrections use linked amendment records [PLANNED]
- REQ-A03: Rider controls data sharing with mechanics — granular consent per inspection [PLANNED]
- REQ-A04: Rider can request deletion of their account and associated images [PLANNED]
- REQ-A05: Audit log records all access to inspection data (who, when, action) [PLANNED]
- REQ-A06: System version, model versions, and provider types are logged per inference run [PLANNED]

---

### M6 — Road Safety Module (Optional, Feature-Flagged)

- REQ-RS01: Module is disabled by default and enabled via a feature flag [PLANNED]
- REQ-RS02: When enabled, rider can activate a "ride monitoring" session [PLANNED]
- REQ-RS03: Driver fatigue monitoring adapted from BharatDrive; single-subject limitation disclosed in UI [PLANNED]
- REQ-RS04: Road hazard detection uses BharatDrive MockDetector (scenario-based) in MVP [PLANNED]
- REQ-RS05: Journey Safety Score displayed only when reliability is HIGH or MEDIUM [PLANNED]
- REQ-RS06: All road-safety outputs labelled "SIMULATION ESTIMATE — research prototype, not a safety certification" [PLANNED]

---

### M7 — Engagement Analytics

- REQ-E01: System tracks: daily active riders, inspections completed, inspections with mechanic review, repeat inspection rate [PLANNED]
- REQ-E02: Analytics dashboard accessible to admin role only [PLANNED]
- REQ-E03: No personally identifiable information in analytics exports [PLANNED]
- REQ-E04: Mechanic participation rate (mechanic reviews / total inspections) is a key metric [PLANNED]
- REQ-E05: Reminder response rate (dismissed / actioned / ignored) tracked per rule [PLANNED]

---

## 4. Acceptance Criteria — MVP

The following criteria define the minimum viable demo:

| # | Criterion | Verified By |
|---|---|---|
| AC-1 | A new rider can register, add a vehicle, upload a tyre image, and receive an analysis report | Manual demo |
| AC-2 | Analysis report displays confidence tiers and uncertainty labels on all AI outputs | UI review |
| AC-3 | System runs with mock provider when real models are absent — no crashes, no blank screens | Automated test |
| AC-4 | A mechanic can log in, view a shared inspection, and record a physical finding | Manual demo |
| AC-5 | AI observations and mechanic findings are visually distinct in the UI | UI review |
| AC-6 | Audit log records every inspection creation and data access event | DB query |
| AC-7 | All maintenance guidance rules are human-readable and visible to the rider | UI review |
| AC-8 | System does not use the word "safe" or "unsafe" as a verdict | Content audit |

---

## 5. Out of Scope for Hackathon

- Real-time video analysis
- Native iOS/Android apps
- Payment or subscription management
- Third-party tyre brand database integration
- OBD-II vehicle sensor integration
- Bluetooth tyre pressure sensor integration
