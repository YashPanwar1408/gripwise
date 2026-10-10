# GripWise — Reuse Decisions

**Date:** 2026-10-10
**Basis:** REPOSITORY_AUDIT.md (source-code inspection of both reference repositories)

All reuse decisions assume the module will be **adapted behind a clean interface**
in the new GripWise codebase, NOT merged wholesale. Reference repositories remain
read-only as specified in the non-negotiable rules.

---

## Decision Legend

| Decision | Meaning |
|---|---|
| REUSE | Adopt with minimal changes; proven logic, clean structure |
| ADAPT | Use as a design reference; rewrite behind a GripWise interface |
| REIMPLEMENT | Replace with new implementation informed by lessons learned |
| EXCLUDE | Do not incorporate; misleading, absent, or out of scope |

---

## 1. From tyreHealth-main

### 1.1 Pipeline Orchestration — ADAPT

**File:** `src/pipeline.py`
**What it does:** Unified `analyse_tyre(image)` entry point; orchestrates detection,
classification, tread, puncture, lifespan sub-modules; picks highest-risk tyre;
returns structured JSON.
**Why adapt, not reuse directly:**
- Pipeline structure and error handling are clean and worth preserving.
- Sub-module interfaces need to be renegotiated (e.g., flat detection is too fragile to pass through unchanged).
- Status codes (ok/monitor/replace/flat_tyre_alert) are useful for GripWise alert logic.
**Action:** Copy orchestration pattern into `gripwise/src/pipeline.py`; replace sub-module
calls behind clean `Protocol`/`ABC` interfaces. Do not import from the reference path.

### 1.2 Tyre Detection (YOLOv8 + Hough fallback) — ADAPT

**File:** `src/detection.py`
**What it does:** Three-tier detection chain: custom YOLO -> pretrained yolov8n.pt -> Hough circles.
**Why adapt:** The fallback chain design is sound. However:
- Custom tyre detector weights are absent; GripWise must train or source its own.
- Vehicle-proxy crop (30% x 25% corner) is fragile; acceptable as a temporary fallback only.
- Environment variable feature flags (TYRE_FAST_MODE, TYRE_ALLOW_PRETRAINED_YOLO) are a good pattern.
**Action:** Adopt the three-tier fallback structure and env-flag pattern. Write a new
`TyreDetector` class in GripWise that wraps YOLO with the same fallback logic.
Train a new tyre-specific YOLO model on real tyre images before shipping.

### 1.3 Tread Analysis (OpenCV edge density) — ADAPT

**File:** `src/tread_analysis.py`
**What it does:** Canny edge density + groove count -> composite tread score 0-100.
**Why adapt:**
- Algorithm structure (CLAHE -> Canny -> morphology -> density) is a reasonable
  starting point for a pixel-based tread proxy.
- Scaling constants are not calibrated. Must be validated against images of known
  tread depth before presenting any output to users.
- Composite weighting (0.32/0.30/0.23/0.15) needs empirical tuning.
**Action:** Port the algorithm to GripWise behind a `TreadAnalyser` interface.
Add explicit uncertainty labels to all outputs. Do NOT present the score as a
tread-depth measurement — only as a relative wear indicator. Document the limitation.

### 1.4 Puncture Detection (Contour + HoughCircles) — REIMPLEMENT

**File:** `src/puncture_detection.py`
**Why reimplement:**
- `flat_tyre = not circle_found` is too fragile; fires on any partially cropped or
  blurred image. A flat-tyre flag must not appear on non-tyre images.
- Dark-anomaly puncture detection has high false-positive risk (dirt, shadows).
- "Crack count" from edge fragments is speculative.
**Action:** Design a new puncture/anomaly module with:
1. Explicit confidence scores rather than binary flags.
2. A minimum image quality gate before flat detection fires.
3. Clear labelling: "anomaly detected" not "puncture confirmed".
Retain the geometric insight (circularity, contour analysis) but add robustness guards.

### 1.5 Lifespan Estimation (RandomForest Regressor) — REIMPLEMENT

**File:** `src/lifespan.py`
**Why reimplement:**
- Trained entirely on synthetic data (hand-written formula + Gaussian noise).
- R2=0.962 is a measure of formula-recovery, not real-world predictive power.
- The 0.86 confidence hardcode is misleading — it implies empirical validation that does not exist.
**Action:** Keep the RandomForest + scikit-learn pipeline architecture (it is clean).
Replace the synthetic data generation with real tyre-wear reference data (e.g., from
manufacturer specifications, SAE standards, or user-validated datasets). Add explicit
uncertainty intervals. Label all output as "estimated" not "predicted".
Until real data is available, use only the heuristic fallback and label it clearly as
a rough guide.

### 1.6 CNN Condition Classifier — EXCLUDE (for now) / REIMPLEMENT

**Files:** `src/classification.py`, `models/classifier/tyre_classifier.h5`
**Why exclude:**
- Model weights are a Git LFS pointer stub; actual weights absent.
- Claimed 100% accuracy is from synthetic toy images — meaningless for real tyres.
- Only 3 classes (Good/Worn/Critical); not trained on any real tyre images.
**Action:** Do not adopt the existing model. Design a new classifier:
1. Start with a pretrained MobileNetV3 or EfficientNet-Lite backbone (transfer learning).
2. Fine-tune on a real tyre image dataset (e.g., Kaggle tyre quality datasets).
3. Target at least 3 classes (Good/Worn/Damaged); add Puncture/Flat as separate
   detection outputs (keep them architecturally separate as tyreHealth does, but validly).
4. Report real held-out test metrics. Never report training-set metrics as accuracy.

### 1.7 Dataset Loader and Synthetic Fallback — ADAPT

**File:** `src/dataset_loader.py`
**What it does:** Clean image loading (Pillow), resizing (224x224 LANCZOS), normalisation
[0,1], stratified split, class-weighted training, synthetic fallback.
**Why adapt:** The loading and splitting code is well-structured. The synthetic fallback
is useful for CI/CD (smoke tests without images) but must not be used for real training.
**Action:** Port `load_images_from_folder`, `split_dataset`, `compute_class_weights` to
GripWise. Remove or clearly gate the synthetic fallback to testing only.

### 1.8 Streamlit Dashboard — ADAPT

**File:** `app/streamlit_app.py`
**Why adapt:** Dashboard layout (condition badge, tread bar, gauge, alert panel) is
appropriate for GripWise. However the file is tightly coupled to tyreHealth internals.
**Action:** Design a new GripWise dashboard importing from the GripWise pipeline only.
Use tyreHealth's UX patterns as a reference for layout and colour coding.

### 1.9 Training Script — ADAPT

**File:** `train.py`
**Why adapt:** The argparse CLI and sequential training (CNN -> regressor -> YOLO) is
a useful pattern. The actual training targets change (new model, real data).
**Action:** Use as a template for `gripwise/train.py`.

---

## 2. From BharatDrive-x-Twin-main

### 2.1 Journey Safety Score Fusion — REUSE

**File:** `fusion/journey_safety.py`
**What it does:** Weighted multi-signal fusion with critical caps, weather degradation,
prediction horizons, and provenance labelling.
**Why reuse:** Clean, pure-Python, stdlib-only function. Well-tested (8 test cases cover
it). Honest labelling (Measured/Estimated/Simulated/Fused). The weighted structure
naturally accommodates adding a tyre-health signal as a new input.
**Action:** Copy `compute_journey_safety()` and `JourneySafety` dataclass into
`gripwise/fusion/journey_safety.py` with attribution. Add a `tyre_risk` input weight
alongside driver readiness and road complexity.

### 2.2 Alert Manager — REUSE

**Files:** `alerts/manager.py`, `alerts/languages.py`
**What it does:** Levels 0-4, cooldown, duplicate suppression, escalation, acknowledgement,
multilingual (English/Hindi/Marathi), optional pygame audio, effectiveness tracking.
**Why reuse:** Elegantly engineered. The dwell-time escalation and reliability-gated
alerting logic are directly applicable to tyre safety alerts. Multilingual support is
a GripWise requirement for Indian market. Pure Python + stdlib.
**Action:** Copy into `gripwise/alerts/` with attribution. Add tyre-specific message
keys (e.g., tyre_critical, tread_warning, puncture_alert).

### 2.3 Counterfactual Simulation Engine — ADAPT

**Files:** `simulation/engine.py`, `simulation/physics.py`
**What it does:** 60-rollout Monte Carlo, 9 actions, physics-aware risk, seeded,
fully reproducible, honest "SIMULATION ESTIMATE" labelling.
**Why adapt:** The simulation is currently vehicle-dynamics focused. For GripWise
(tyre safety + rider trust), it needs a tyre-degradation dimension added (e.g., risk
increases with worn tyre, wet road, high speed).
**Action:** Port the CounterfactualEngine and physics to GripWise. Add tyre_risk as
a fatigue-analog that scales collision risk and extends stopping distance.

### 2.4 Driver Monitoring Pipeline — REUSE (if rider monitoring is in scope)

**Files:** All of `driver_monitoring/`
**Why reuse:** This is the strongest code in either repository — well-calibrated,
well-tested, honestly documented, with 5 documented defect-fixes. The personal
fatigue signature, reliability engine, and state machine are production-quality.
**Caveat:** Single-subject evaluation; subject-independent performance unknown.
**Action:** If GripWise includes rider-fatigue monitoring, copy the entire
`driver_monitoring/` package into `gripwise/driver_monitoring/` with attribution.
Do not modify the core algorithm until a multi-subject evaluation is done.

### 2.5 SQLite Persistence — REUSE

**File:** `storage/db.py`
**What it does:** WAL-mode SQLite, 7 structured tables, session reports, privacy guards,
JSON export. Well-tested (SQLite roundtrip test in test_simulation_fusion.py).
**Why reuse:** Directly applicable to GripWise session recording. Add a `tyre_event`
table for tread scores and replacement alerts.
**Action:** Copy `Store` class into `gripwise/storage/db.py`. Extend schema with
tyre-specific tables. Retain all existing privacy guards.

### 2.6 Digital Twin Scenarios — ADAPT

**Files:** `digital_twin/scenarios/*.json`, `digital_twin/world_state.py`
**What it does:** 6 JSON-driven scripted Indian road scenarios for demo and testing.
**Why adapt:** Scenario format is clean and extensible. GripWise needs tyre-specific
scenario parameters (tread_score, tyre_pressure, road_surface_type).
**Action:** Extend WorldState with tyre health fields. Create new GripWise scenarios
(worn_tyre_highway, low_pressure_rural_road, puncture_on_ghat).

### 2.7 Context Providers (Weather, Map, Sensor) — REUSE

**File:** `context_providers.py`
**Why reuse:** Clean abstraction for offline-first context. Weather friction data is
directly relevant to tyre-grip simulation (wet road + worn tyre = high risk).
**Action:** Copy into `gripwise/context_providers.py` with attribution. Use weather
friction values as a multiplier in the tyre-risk computation.

### 2.8 Road Hazard Detection (YoloDetector + MockDetector) — REUSE

**Files:** `road_perception/detection.py`, `road_perception/road_complexity.py`
**Why reuse:** Well-designed detector abstraction with honest distance labelling.
Road complexity is a useful contextual signal for tyre wear rate (rough/complex roads
accelerate tyre degradation).
**Action:** Copy into `gripwise/road_perception/` with attribution. Road complexity
index can feed into GripWise tyre-wear simulation as a road-surface harshness signal.

### 2.9 Web Dashboard (stdlib server) — ADAPT

**Files:** `dashboard/server.py`, `dashboard/static/`
**Why adapt:** Zero-dependency Python stdlib HTTP server is ideal for the GripWise
offline-first target. UI layout needs redesigning for tyre-centric data.
**Action:** Keep server.py; redesign static/ with tyre health panels.

---

## 3. Priority Order for GripWise MVP

The following components should be built/adopted in this order for the smallest
valuable MVP:

| Priority | Component | Decision | Effort |
|---|---|---|---|
| 1 | Pipeline orchestration | ADAPT from tyreHealth | Low |
| 2 | Tyre detection (YOLO + fallback) | ADAPT from tyreHealth | Medium |
| 3 | Tread analysis | ADAPT from tyreHealth | Low |
| 4 | Alert manager + multilingual | REUSE from BharatDrive | Low |
| 5 | SQLite persistence | REUSE from BharatDrive | Low |
| 6 | Journey Safety Score fusion | REUSE from BharatDrive | Low |
| 7 | Context providers (weather) | REUSE from BharatDrive | Low |
| 8 | Streamlit / stdlib dashboard | ADAPT from both | Medium |
| 9 | Puncture / flat detection | REIMPLEMENT | Medium |
| 10 | CNN condition classifier | REIMPLEMENT (new model, real data) | High |
| 11 | Lifespan estimation | REIMPLEMENT (real data) | High |
| 12 | Driver/rider fatigue monitoring | REUSE from BharatDrive | Low (code) |
| 13 | Simulation engine | ADAPT from BharatDrive | Medium |
| 14 | Scenarios | ADAPT from BharatDrive | Low |

---

## 4. What NOT To Do

1. Do NOT use the lifespan_model.pkl in production without retraining on real data.
2. Do NOT report the 1.0 accuracy metric — it is derived from synthetic training.
3. Do NOT present the tread score as an absolute depth measurement in mm.
4. Do NOT trust the flat-tyre flag without additional confidence gating.
5. Do NOT ship the CNN classifier without real training data and held-out validation.
6. Do NOT claim the km-remaining estimate is validated without real-world data.
