# GripWise — Dependency Matrix

Generated: 2026-10-10
Source: Inspection of requirements.txt files and import statements in both reference repositories.

---

## 1. tyreHealth-main Dependencies

### 1.1 requirements.txt (as specified)

| Package | Constraint | Category | Required For |
|---|---|---|---|
| ultralytics | >=8.3.0 | CV/ML | YOLOv8 tyre detection |
| opencv-python | >=4.8.0 | CV | Tread analysis, puncture detection, fallback detection, image I/O |
| tensorflow | >=2.13.0 | Deep Learning | CNN condition classifier (Keras) |
| scikit-learn | >=1.3.0 | ML | RandomForest lifespan regressor, class weights, train_test_split |
| streamlit | >=1.28.0 | UI | Streamlit dashboard |
| numpy | >=1.24.0 | Numerics | All modules |
| matplotlib | >=3.7.0 | Visualisation | Training curves, chart rendering |
| Pillow | >=10.0.0 | Image I/O | dataset_loader.py image opening |
| plotly | >=5.18.0 | Charts | Streamlit dashboard gauges |
| pyyaml | >=6.0 | Config | YOLO dataset.yaml generation |
| joblib | >=1.3.0 | Persistence | lifespan_model.pkl save/load |
| pytest | >=8.2.0 | Testing | Test runner only |

### 1.2 Implicit / Undeclared Dependencies

| Package | Where Used | Notes |
|---|---|---|
| torch (PyTorch) | detection.py `_resolve_device()` | Optional — imported only for CUDA check |
| yaml | detection.py | Covered by pyyaml |

### 1.3 Python Version

- Minimum: **Python 3.10** (uses `str | Path` union type syntax throughout)
- Tested range: Not documented
- GPU: Optional; TensorFlow and ultralytics auto-detect CUDA

### 1.4 Known Compatibility Concerns

| Issue | Details |
|---|---|
| TensorFlow vs PyTorch | Both tensorflow (for Keras CNN) and torch (via ultralytics YOLO) required simultaneously. Can cause CUDA version conflicts. |
| tensorflow>=2.13 on Python 3.11+ | TF 2.13 has limited Python 3.11 support; 3.12 is not supported by TF<2.16. |
| ultralytics + tensorflow GPU | Competing for GPU memory; may require explicit device assignments. |
| No version pins | All dependencies use >= only; no upper bounds. Future breaking changes possible. |

---

## 2. BharatDrive-x-Twin-main Dependencies

### 2.1 requirements.txt (as specified — mostly commented)

| Package | Constraint | Status | Category | Required For |
|---|---|---|---|---|
| numpy | >=1.23 | Recommended (active) | Numerics | All modules |
| opencv-python | >=4.7 | Recommended (active) | CV | Camera capture, solvePnP head pose, image quality |
| mediapipe | >=0.10 | Optional (commented) | Landmark | FaceMesh landmark backend |
| face_recognition | ==1.3.0 | Optional (commented) | Landmark | dlib-based landmark backend |
| ultralytics | >=8.0 | Optional (commented) | CV/ML | YOLOv8 road hazard detection |
| pygame | >=2.5 | Optional (commented) | Audio | Non-blocking alarm audio |
| scikit-learn | >=1.3 | Optional (commented) | ML | Evaluation / diagnostics only |
| pytest | >=7.0 | Dev | Testing | Test runner |

### 2.2 Core (No External Deps)

The following modules run on **Python stdlib + numpy + opencv only**:
- fusion/journey_safety.py (stdlib only)
- simulation/engine.py (stdlib only)
- simulation/physics.py (stdlib only)
- alerts/manager.py (stdlib + optional pygame)
- alerts/languages.py (stdlib only)
- digital_twin/world_state.py (stdlib only)
- storage/db.py (stdlib sqlite3 only)
- dashboard/server.py (stdlib http.server only)
- context_providers.py (stdlib only)
- All 6 scenario JSON files

### 2.3 Python Version

- Supported: **Python 3.10–3.12** (per README badges)
- Core (stdlib) runs on 3.9+; optional deps set the floor at 3.10

### 2.4 Known Compatibility Concerns

| Issue | Details |
|---|---|
| face_recognition==1.3.0 | Requires dlib (C++ build); complex install on Windows without pre-built wheels. |
| mediapipe vs face_recognition | Both provide facial landmarks; only one active at a time. |
| ultralytics Python range | ultralytics>=8.0 supports Python 3.8-3.12; no conflict. |
| No version pins | numpy and opencv use >= only; upper bounds missing. |

---

## 3. GripWise — Recommended Dependency Stack

If GripWise adopts the reuse decisions in REUSE_DECISIONS.md, the minimal dependency set is:

### 3.1 Core (Required)

| Package | Recommended Version | Source | Notes |
|---|---|---|---|
| Python | 3.11 | — | Stable LTS; supported by all deps |
| numpy | >=1.26,<2.0 | Both repos | Pin upper bound for stability |
| opencv-python | >=4.9,<5.0 | Both repos | Core CV pipeline |
| ultralytics | >=8.3,<9.0 | tyreHealth | YOLOv8 tyre detection |
| scikit-learn | >=1.4,<2.0 | tyreHealth | Lifespan regressor |
| joblib | >=1.3 | tyreHealth | Model persistence |
| pyyaml | >=6.0 | tyreHealth | YOLO yaml config |

### 3.2 Driver Monitoring (If Adopted from BharatDrive)

| Package | Recommended Version | Notes |
|---|---|---|
| mediapipe | >=0.10.14 | FaceMesh landmark backend |
| opencv-python | (already listed) | head pose solvePnP |

### 3.3 Dashboard

| Package | Recommended Version | Notes |
|---|---|---|
| streamlit | >=1.32,<2.0 | If adopting tyreHealth dashboard style |
| plotly | >=5.18,<6.0 | Dashboard gauges |

### 3.4 NOT Recommended for GripWise

| Package | Reason |
|---|---|
| tensorflow / keras | Only needed if CNN classifier is adopted; weights absent; large dependency. Prefer ONNX export of any retrained model. |
| face_recognition==1.3.0 | dlib build complexity on Windows. Use mediapipe instead. |
| pygame | Optional audio; add only if alert audio is a confirmed requirement. |

---

## 4. Conflict Analysis

| Conflict | Risk | Mitigation |
|---|---|---|
| TF + PyTorch (via ultralytics) in same venv | Medium | Use CPU-only torch for ultralytics or containerise. |
| numpy <2.0 vs newer ultralytics | Low | Pin numpy<2.0 explicitly. |
| mediapipe + opencv version mismatch | Low | Test specific mediapipe+opencv combo before locking. |
| Python 3.12 + tensorflow | HIGH (if TF adopted) | TF 2.16+ needed for Python 3.12; drop TF if possible. |
