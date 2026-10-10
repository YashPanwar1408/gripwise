# GripWise

GripWise is an AI-assisted tyre-safety and rider-trust platform built for the **Tata Imagination Challenge** and **Eurogrip TORQ Challenge 4.0**.

It bridges the gap between everyday riders and professional mechanics by providing explainable AI tyre inspections, secure data sharing, and verifiable mechanic interventions.

## Product Modules

1. **Rider Workspace**: Register vehicles, upload tyre images for AI inspection, and review safety guidance.
2. **Tyre Intelligence**: Pluggable AI inference supporting both deterministic MOCK modes for demos, and OpenCV pipelines for real image analysis.
3. **Mechanic Workspace (Phase 3 Backend Ready)**: Riders can grant explicit consent for mechanics to view their AI reports and append verified physical findings (e.g., actual tread depth measurements, service records).

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
