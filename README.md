# GripWise

GripWise is an AI-assisted tyre-safety and rider-trust platform built for the **Tata Imagination Challenge** and **Eurogrip TORQ Challenge 4.0**.

It bridges the gap between everyday riders and professional mechanics by providing explainable AI tyre inspections, secure data sharing, and verifiable mechanic interventions.

## Product Modules

1. **Rider Workspace**: Register vehicles, upload tyre images for AI inspection, review plain-language safety guidance, and manage mechanic consent.
2. **Tyre Intelligence**: Pluggable AI inference supporting both deterministic MOCK modes for testing and OpenCV pipelines for tread proxy and anomaly detection.
3. **Mechanic Workspace**: Consent-based service queue where mechanics review authorized rider inspections, document physical gauge measurements (depth mm, PSI), and record service history.
4. **GripWise Saathi — Mechanic Advocacy & Engagement (Eurogrip TORQ Challenge 4.0, Case Study 4)**:
   - **Professional Profile**: Stored workshop records with a real profile-completion indicator.
   - **Tyre-Care Learning Hub**: 5 structured educational modules with interactive technical quizzes (ISO/ETRTO guidance; zero brand bias).
   - **Verifiable Recognition & Badges**: Transparent participation tiers (Bronze, Silver, Gold, Master Saathi) and digital badges with deterministic, idempotent scoring.
   - **Customer Engagement & Referrals**: Consent-aware customer tyre safety follow-up tracking with privacy preservation.
   - **Eurogrip TORQ 4.0 Concept**: Proposed tool-support initiatives (digital tread depth gauges, calibrated tyre pressure stations, workshop safety wallcharts, and compound masterclasses).

## Architecture
- **Frontend**: Next.js (App Router), React, Tailwind CSS, TypeScript.
- **Backend**: FastAPI, Python 3.13, SQLite + async SQLAlchemy.
- **Testing**: Pytest, AsyncClient.

## Quickstart

### Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Running the Tests
GripWise boasts a rigorous, isolated test suite that verifies all core logic without relying on external dependencies. Run from the project root:
```bash
python -m pytest backend/tests/ -v
python -m pytest ai/tests/ -v
```

## Documentation
- [Implementation Status](docs/IMPLEMENTATION_STATUS.md)
- [Test Report](docs/TEST_REPORT.md)
- [Known Limitations](docs/KNOWN_LIMITATIONS.md)
- [Demo Script](docs/DEMO_SCRIPT.md)
- [Licence & Attribution](docs/LICENCE_AND_ATTRIBUTION.md)
