# GripWise — Repository Audit

**Audit date:** 2026-10-10
**Auditor:** Senior Software Architect / Repository Auditor (AI-assisted)
**Scope:** `gripwise/refrences/BharatDrive-x-Twin-main/` and `gripwise/refrences/tyreHealth-main/`
**Method:** Direct source-code inspection only. No commands were executed. No tests were run.

> **Classification key**
> - **VERIFIED FROM SOURCE** — confirmed by reading the actual code
> - **UNVERIFIED** — claimed in README but not independently validated
> - **NOT IMPLEMENTED** — file or feature absent from the repository
> - **TESTED** — a test suite exists that covers this behaviour (NOT run by this auditor)

---

## Part 1 — tyreHealth-main

### 1.1 Overview

A five-stage computer-vision pipeline for tyre health analysis served through a Streamlit dashboard.
Authors: Adesh Kumar Shukla, Krissh Gera. No licence file found in the repository.

### 1.2 Directory Structure (Actual)

```
tyreHealth-main/
├── src/
│   ├── dataset_loader.py      (8.6 KB)  Image loading, normalisation, synthetic fallback
│   ├── detection.py          (10.4 KB)  YOLOv8 tyre detector + Hough-circle fallback
│   ├── classification.py      (9.9 KB)  Keras CNN condition classifier
│   ├── tread_analysis.py      (3.4 KB)  OpenCV Canny tread scoring
│   ├── puncture_detection.py  (4.5 KB)  Contour + HoughCircle anomaly detection
│   ├── lifespan.py            (5.6 KB)  scikit-learn RandomForest regression
│   └── pipeline.py            (6.6 KB)  Unified analyse_tyre() entry point
├── app/
│   └── streamlit_app.py      (21.4 KB)  Streamlit dashboard
├── models/
│   ├── classifier/
│   │   ├── tyre_classifier.h5   <- GIT-LFS POINTER (134 B stub; 287 MB actual absent)
│   │   └── training_metrics.json  (accuracy=1.0 — see critical flag)
│   └── regression/
│       ├── lifespan_model.pkl   (3.2 MB — present and loadable)
│       └── training_metrics.json (R2=0.962 on synthetic data)
├── tests/
│   ├── test_pipeline.py      (4.1 KB — 3 monkeypatched tests)
│   └── run_tests.py          (195 B)
├── train.py                  (1.8 KB)
├── yolov8n.pt                (6.3 MB — pretrained general detector, present)
└── requirements.txt
```

### 1.3 Capability Assessment

#### A. Tyre Detection and Classification

**Detection — VERIFIED FROM SOURCE** (`src/detection.py`)

`detect_tyres(image)` three-tier fallback:
1. Custom `models/yolo/tyre_detector.pt` — **FILE DOES NOT EXIST** in this workspace
2. Pretrained `yolov8n.pt` (general COCO detector, not tyre-specific); COCO vehicle
   classes used as proxy — tyre boxes inferred as bottom-corner 30% x 25% crops of
   vehicle bounding boxes. This is a geometric heuristic, not tyre detection.
3. `detect_tyre_opencv()` — Hough circles; will misfire on scene images.

**Classification — UNVERIFIED** (`src/classification.py`, model weights absent)

- CNN: Conv32->Pool->Conv64->Pool->Dropout(0.3)->Dense128->Dense3(softmax)
- Classes: Good / Worn / Critical **(3 classes only, not 5 as README claims)**
  Puncture and Flat are handled by a separate module, NOT by the CNN.
- `tyre_classifier.h5` is a **Git LFS pointer stub** (134 bytes).
  The 287 MB actual weights are NOT present in this workspace.
- Fallback `_fallback_classification()` uses edge-ratio thresholds (>0.17 Good,
  >0.08 Worn, else Critical). Real-world accuracy unknown.

> **CRITICAL FLAG — training_metrics.json: accuracy=1.0, precision=1.0, recall=1.0**
> 360 samples (288 train, 72 val). `generate_synthetic_samples()` creates toy images
> (dark circles with line patterns). These metrics do NOT reflect real-world performance.
> Status: **UNVERIFIED as meaningful**.

#### B. Tread / Groove Analysis — VERIFIED FROM SOURCE (`src/tread_analysis.py`)

`analyze_tread(roi)` pipeline:
1. Grayscale + Gaussian blur (5x5)
2. Canny edges (low=45, high=140) + morphological closing (3x3)
3. Edge density = edge_pixels / total_pixels
4. Groove count = median transitions across 8 horizontal strips
5. Composite tread score (0-100):
   `0.32 * edge_score + 0.30 * groove_score + 0.23 * texture_score + 0.15 * contrast_score`

**Limitations:**
- Scaling constants (420x, 7.5x, /16, 2.4x) are hand-tuned with no calibration
  against actual depth measurements in mm.
- Image angle, lighting, and distance produce different scores for the same tread depth.
- No correlation with legal minimum depth (~1.6 mm) demonstrated.
- Returns 50.0 on error — a sentinel masquerading as a plausible value.

**Status: UNVERIFIED as a real depth proxy. Visually motivated but not physically calibrated.**

#### C. Puncture and Flat-Tyre Detection — VERIFIED FROM SOURCE (`src/puncture_detection.py`)

`detect_puncture_and_flat(roi)`:
1. **Puncture:** Thresholds dark pixels (<52 brightness), finds contours in size
   range 0.008%-1.2% of image area with circularity >0.15. High false-positive risk
   for dirt, shadows, dark rubber markings.
2. **Flat detection:** `flat_tyre = not circle_found` from HoughCircles.
   Fires whenever a circle cannot be detected — extremely fragile on any out-of-focus,
   partially cropped, or non-round image.
3. **Crack count:** Connected-component fragments sized 10-200 px in Canny edge map.
   Normal tyre tread produces hundreds of such components; label "crack" is speculative.

**Status: UNVERIFIED. Geometrically motivated but untested against real imagery.
High false-positive risk, especially for flat detection.**

#### D. Remaining-Distance / Lifespan Estimation — VERIFIED FROM SOURCE (UNVERIFIED for accuracy)

`predict_lifespan(tread_depth_score, crack_count, condition)` (`src/lifespan.py`):
- Uses `lifespan_model.pkl` (3.2 MB RandomForest — **present and loadable**)
- **CRITICAL FLAG:** Regressor trained entirely on synthetic data from
  `generate_training_data()`:
    remaining_km = tread_depth * 520.0 + condition * 9500.0 - crack_count * 1650.0 + noise(0, 2500)
  This is a hand-written formula with Gaussian noise, not real tyre-wear measurements.
- R2=0.962, MAE=2,355 km reflect recovery of the synthetic formula, not real-world accuracy.
- Confidence hardcoded to 0.86 (model) or 0.5 (heuristic).

**Status: UNVERIFIED. km estimate is a synthetic-formula output.
Do not present as a factual prediction to users.**

#### E. Driver Fatigue — NOT IMPLEMENTED in tyreHealth-main.
#### F. Road-Hazard Detection — NOT IMPLEMENTED in tyreHealth-main.
#### G. Risk Fusion and Simulation — NOT IMPLEMENTED in tyreHealth-main.

#### H. Dashboard, API, Persistence, Tests

**Dashboard — VERIFIED FROM SOURCE**
- `app/streamlit_app.py` (21.4 KB): Streamlit UI with image upload, webcam capture,
  condition badge, tread bar, gauges, alert panel, training metrics.
- Entry: `streamlit run app/streamlit_app.py` -> http://localhost:8501
- No authentication, no deployment configuration.

**Programmatic API — VERIFIED FROM SOURCE**
```python
from src.pipeline import analyse_tyre
result = analyse_tyre(image_bgr)
# Returns: condition, tread_score, remaining_km, status, alerts, tyres, detections, inference_ms
```

**Persistence:** None — no database. Results are in-memory only.

**Tests — VERIFIED FROM SOURCE (NOT RUN)**
- 3 pytest tests using monkeypatch to mock ALL sub-modules.
- Tests validate pipeline routing logic only, NOT CV algorithm correctness.

### 1.4 Dependencies

| Package | Min Version | Notes |
|---|---|---|
| ultralytics | 8.3.0 | YOLOv8 runtime |
| opencv-python | 4.8.0 | Core CV |
| tensorflow | 2.13.0 | Keras CNN |
| scikit-learn | 1.3.0 | Regression |
| streamlit | 1.28.0 | Dashboard |
| numpy | 1.24.0 | — |
| matplotlib | 3.7.0 | Visualisation |
| Pillow | 10.0.0 | Image I/O |
| plotly | 5.18.0 | Dashboard charts |
| pyyaml | 6.0 | YOLO yaml |
| joblib | 1.3.0 | Model pickling |
| pytest | 8.2.0 | Tests only |

Python 3.10+ required.

### 1.5 Model Weights and Datasets

| Asset | Present | Notes |
|---|---|---|
| yolov8n.pt (6.3 MB) | YES | Pretrained general detector |
| models/yolo/tyre_detector.pt | NO | Custom tyre detector missing |
| models/classifier/tyre_classifier.h5 | NO (LFS stub) | 287 MB actual weights absent |
| models/regression/lifespan_model.pkl | YES (3.2 MB) | Trained on synthetic data only |
| data/raw/ images | NO | No training images present |
| data/annotations/ | NO | No YOLO annotation labels present |

### 1.6 Known Failure Modes

1. Classifier absent: edge-ratio heuristic fallback; real-world accuracy unknown.
2. Flat detection: fires whenever HoughCircles fails; very high false-positive rate on real photos.
3. Lifespan: entirely synthetic training — outputs look plausible but have no empirical grounding.
4. 1.0 accuracy metric: trained on synthetic toy images; meaningless for real tyre images.
5. No tyre-specific YOLO: vehicle-proxy crop is a rough approximation.
6. No dataset present: cannot retrain or validate without sourcing external images.

---

## Part 2 — BharatDrive-x-Twin-main

### 2.1 Overview

An offline-first AI safety co-pilot for Indian roads. Fuses driver-facing camera (fatigue
monitoring) with road-facing camera (hazard detection) into a Journey Safety Score with
adaptive multilingual alerts, Monte-Carlo counterfactual simulation, SQLite persistence,
and a zero-dependency web dashboard. Author: Shreepad Salvi (CODEX038).
No licence file present.

### 2.2 Directory Structure (Actual)

```
BharatDrive-x-Twin-main/
├── app/
│   ├── main.py          (27.1 KB)  CLI: --demo | --live | --road | --legacy
│   └── config.py         (3.3 KB)  Config dataclass + .env loading
├── driver_monitoring/    (13 files, ~60 KB total)
│   ├── landmarks.py       (7.6 KB)  MediaPipe/face_recognition/Synthetic backends
│   ├── eye_analysis.py    (2.0 KB)  EAR per-eye, smoothed
│   ├── blink_analysis.py  (3.2 KB)  Blink rate, long blinks, microsleep flag
│   ├── yawn_analysis.py   (2.7 KB)  MAR + sustained-opening yawn detector
│   ├── perclos.py         (1.8 KB)  PERCLOS for configurable windows
│   ├── head_pose.py       (3.8 KB)  solvePnP pitch/yaw/roll + EWMA nod detection
│   ├── fatigue_signature.py (5.3 KB) Personal baseline + 3xMAD outlier rejection
│   ├── forecasting.py     (6.0 KB)  Hand-weighted risk model + temporal forecaster
│   ├── readiness_engine.py (2.6 KB) 0-100 readiness score, rate-limited
│   ├── reliability.py     (3.2 KB)  Image quality + occlusion reliability engine
│   ├── state_machine.py   (4.2 KB)  Dwell-time FSM (ALERT->DROWSY->CRITICAL)
│   └── pipeline.py        (7.3 KB)  DriverMonitor.update() — one call per frame
├── road_perception/
│   ├── detection.py       (8.0 KB)  MockDetector (scenario JSON) + YoloDetector
│   ├── tracking.py        (3.4 KB)  IoU tracker
│   └── road_complexity.py (4.6 KB)  Road Complexity Index (0-100)
├── fusion/
│   └── journey_safety.py  (3.8 KB)  compute_journey_safety() -> JourneySafety
├── simulation/
│   ├── engine.py          (9.2 KB)  CounterfactualEngine (60-rollout Monte Carlo)
│   └── physics.py         (1.5 KB)  TTC, braking/stopping distance
├── alerts/
│   ├── manager.py         (6.2 KB)  AlertManager levels 0-4, cooldown, escalation
│   └── languages.py       (3.6 KB)  English / Hindi / Marathi messages
├── digital_twin/
│   ├── world_state.py     (3.2 KB)  WorldState + scenario loader
│   └── scenarios/         6 JSON files (cattle, motorcycle_cut_in, pothole, etc.)
├── storage/
│   └── db.py              (7.0 KB)  SQLite WAL — 7 tables
├── dashboard/
│   ├── server.py          (1.8 KB)  Zero-dependency stdlib HTTP server port 8765
│   └── static/            HTML/JS dashboard assets
├── context_providers.py   (6.1 KB)  Map/Weather/CCTV/SensorHub providers
├── tests/
│   ├── test_driver_monitoring.py  (6.8 KB)  12 synthetic tests
│   ├── test_simulation_fusion.py  (5.0 KB)  8 tests (physics, scenarios, fusion, alerts, SQLite)
│   ├── test_road_and_context.py   (2.8 KB)
│   └── test_end_to_end_demo.py    (1.3 KB)
└── docs/
    ├── EVALUATION_LOG.md  (8.1 KB)  Honest measured results with per-class tables
    ├── DESIGN.md          (9.9 KB)  Full system design
    └── AUDIT_REPORT.md    (9.4 KB)  Author self-audit
```

### 2.3 Capability Assessment

#### A-D. Tyre-Specific Capabilities

**Status: NOT IMPLEMENTED in BharatDrive.**
Road detector handles Indian hazards (potholes, cattle, pedestrians, vehicles) but has
no tyre-specific detection, tread analysis, puncture detection, or lifespan estimation.

#### E. Driver Fatigue / Readiness Monitoring — VERIFIED FROM SOURCE

Complete pipeline in `driver_monitoring/`:

| Sub-module | What it actually does |
|---|---|
| landmarks.py | MediaPipe FaceMesh / face_recognition / Synthetic backends; geometric only |
| eye_analysis.py | Eye Aspect Ratio (EAR) per-eye, smoothed |
| blink_analysis.py | Blink rate per min, long-blink duration, microsleep flag |
| yawn_analysis.py | MAR + sustained >= 1.5 s (rejects speech false positives) |
| perclos.py | PERCLOS for 30/60 s windows |
| head_pose.py | cv2.solvePnP pitch/yaw/roll + EWMA nod smoothing |
| fatigue_signature.py | Per-session personal baseline, 3xMAD rejection, MAD floor at 8% of median |
| forecasting.py | Hand-weighted heuristic risk (0-1) + temporal trend + horizon estimate |
| readiness_engine.py | 0-100 readiness score, rate-limited to prevent violent jumps |
| reliability.py | Image quality (brightness/blur) + occlusion; gates all downstream decisions |
| state_machine.py | Dwell-time FSM: ALERT->PRE_DROWSY->DROWSY->CRITICAL |
| pipeline.py | DriverMonitor.update(frame_bgr, ts) -> DriverFrameResult dataclass |

**Measured calibration (docs/EVALUATION_LOG.md):**
- 4 live self-test sessions (single subject, laptop webcam, MediaPipe, i7-14650HX)
- 5 specific defects found and fixed (MAD floor, circular baseline lock, nod jitter,
  critical dwell, alert message split)
- After fixes: max risk 0.927 -> 0.647; L4 alert storms eliminated under good lighting
- Known residual: intermittent L2 CAUTION on awake driver (MediaPipe vs dlib EAR scale)
- Limitation: single-subject evaluation only; no LOSO validation

**Status: VERIFIED FROM SOURCE. Robustly implemented with documented calibration and honest limitations.**

#### F. Road-Hazard Detection — VERIFIED FROM SOURCE (model file status unknown)

`road_perception/detection.py`:
- YoloDetector: loads `models/indian_hazards.pt` if present; falls back to yolov8n.pt
- 20 Indian road classes; COCO->project class mapping
- Monocular distance estimation (pinhole formula) explicitly labelled "ESTIMATED"
- MockDetector: plays back scenario JSON — functional without any ML dependency

`models/indian_hazards.pt` metrics from EVALUATION_LOG.md (UNVERIFIED — file possibly absent):

| Metric | Value |
|---|---|
| Training data | IDD Detection + RDD2022 India |
| Train/Val images | 7,382 / 1,648 |
| Overall mAP50 | 0.442 |
| Inference speed (CPU) | 24.6 ms/image |
| Strong classes | truck 0.75, motorcycle 0.67, car 0.60 |
| Weak classes | cattle 0.21 (low recall), bicycle 0.24, traffic_light 0.00 (3 val samples) |
| Missing classes | speed_breaker, waterlogging, open_manhole, wrong_side_vehicle |

**Status: VERIFIED FROM SOURCE (design and code). Model weights not confirmed present.**

#### G. Risk Fusion and Simulation — VERIFIED FROM SOURCE

`fusion/journey_safety.py` — `compute_journey_safety()`:
- Weighted combination: readiness (0.35) + road complexity (0.30) + hazard safety (0.20) +
  simulation best-action (0.15)
- Critical caps: readiness <= 20 -> score cap 25; max_hazard >= 0.85 -> cap 40
- Output: JourneySafety dataclass (score 0-100, danger_level, confidence, reasons, horizons)

`simulation/engine.py` — CounterfactualEngine (60-rollout Monte Carlo):
- 9 candidate actions; physics: TTC, stopping distance, friction, reaction time
- Seeded RNG (seed=7) -> fully reproducible
- All outputs labelled "SIMULATION ESTIMATE — not a guaranteed outcome"

**Status: VERIFIED FROM SOURCE. Well-engineered with honest provenance labelling.**

#### H. Dashboard, API, Persistence, Tests — VERIFIED FROM SOURCE

- dashboard/server.py: Pure stdlib HTTP server, port 8765, WebSocket live updates
- storage/db.py: SQLite WAL, 7 tables; no raw video stored by default
- 4 test files, ~20 tests total, synthetic/deterministic, no camera required
- Entry: `python -m app.main --demo --dashboard` / `pytest tests/`

### 2.4 Dependencies

| Package | Status | Notes |
|---|---|---|
| numpy>=1.23 | Recommended | — |
| opencv-python>=4.7 | Recommended | Camera, solvePnP, image quality |
| mediapipe>=0.10 | Optional (commented) | Landmark backend |
| face_recognition==1.3.0 | Optional (commented) | Alternative backend |
| ultralytics>=8.0 | Optional (commented) | YOLO road detector |
| pygame>=2.5 | Optional (commented) | Audio alerts |
| scikit-learn>=1.3 | Optional (commented) | Evaluation |
| pytest>=7.0 | Dev | Tests |

Python 3.10-3.12. Core runs on stdlib + numpy + opencv only.

### 2.5 Model Weights and Datasets

| Asset | Present | Notes |
|---|---|---|
| models/indian_hazards.pt | UNKNOWN | Not in directory listing; may need Git LFS pull |
| yolov8n.pt | Auto-downloaded | Via ultralytics at runtime |
| MediaPipe models | Auto-downloaded | At runtime |
| IDD/RDD2022 datasets | NO | Only datasets/registry.json metadata present |
| 6 scenario JSON files | YES | Fully scripted Indian road scenarios |

### 2.6 Known Failure Modes

1. Single-subject calibration: thresholds may not generalise across drivers.
2. MediaPipe EAR scale mismatch: residual false L2 alerts on awake driver.
3. Road camera: video-file only — no live dashcam capture path.
4. Cattle/bicycle recall: very low mAP50; hazardous objects frequently missed.
5. Monocular distances: approximate; not suitable for precise measurements.
6. indian_hazards.pt absent: full road detection requires custom weights.

---

## Part 3 — README vs Source Discrepancies

### tyreHealth-main

| README Claim | Source Reality |
|---|---|
| "5-class classifier (Good/Worn/Critical/Puncture/Flat)" | 3 classes only; Puncture/Flat are in a separate module. |
| "CNN fine-tuned on pretrained backbone" | Trained from scratch; no transfer learning. |
| "production-grade" | No real dataset, no actual model weights, no deployment config. |
| "100% accuracy, precision, recall" | Trained on synthetic toy images; meaningless for real tyres. |
| "scikit-learn Random Forest or Ridge Regression" | CODE: always RandomForest; Ridge is not used. |

### BharatDrive-x-Twin-main

| README Claim | Source Reality |
|---|---|
| "No cloud, no API keys, no GPU" | Accurate — all external sources are optional. |
| "mAP50 0.442, 10 classes" | Documented in EVALUATION_LOG with per-class table and honest caveats. UNVERIFIED (file possibly absent). |
| "Zero-dependency dashboard" | Accurate — pure stdlib HTTP server confirmed in code. |
| "Seeded Monte-Carlo simulation" | Accurate — seed=7 confirmed in engine.py. |
| "25 FPS, 12 ms loop latency" | UNVERIFIED — no benchmark code found. |

---

## Part 4 — Inspection Limitations

1. Tests not executed. Pass/fail status is UNVERIFIED.
2. `indian_hazards.pt` not confirmed present; may require Git LFS pull.
3. Streamlit dashboard inspected at source level only; not rendered.
4. No real tyre images available; CV algorithm quality assessed by logic only.
5. Single-pass code reading; complex calibration interactions not simulated.
