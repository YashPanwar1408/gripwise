# GripWise

GripWise is an independent tyre-safety and preventive-maintenance platform for riders and two-wheeler workshops. Riders can keep vehicle and inspection records, understand maintenance guidance, and share inspection access with a workshop only after granting consent. Mechanics can review authorized inspections, record physical findings and service history, and use Mechanic Growth for learning, profile completion, recognition, and consent-aware follow-ups.

GripWise is a prototype. The default inspection provider is `mock`, which returns simulated demonstration results and does not analyze the uploaded image. The interface identifies these results as demo output. The optional computer-vision provider requires additional model dependencies and has not been validated as a safety instrument. Do not rely on prototype output instead of a physical tyre inspection by a qualified mechanic.

## Product areas

- **Rider workspace:** vehicles, tyre inspection reports, maintenance history, and control over workshop access.
- **Workshop workspace:** a consent-controlled service queue, Workshop ID sharing, physical inspection findings, and service records.
- **Mechanic Growth:** workshop profile completion, general tyre-care learning modules and quizzes, activity recognition, and consent-aware customer follow-ups. Recognition is based on recorded GripWise activity and is not an independent certification.
- **Optional Partner Programmes:** proposal examples that are hidden by default. They do not represent an approved offer, partnership, sponsorship, funding, or accreditation.

## Run locally on Windows

Prerequisites: Python 3.13, Node.js/npm, and Docker Desktop.

From the project root, start PostgreSQL:

```powershell
docker compose up -d db
```

In a second terminal, install the backend dependencies and start FastAPI:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

In a third terminal, start Next.js:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>. FastAPI documentation is at <http://localhost:8000/api/docs>. Keep the database running while using the app. Stop it with `docker compose down` from the project root; this preserves the named PostgreSQL volume. Use `docker compose down -v` only if you intentionally want to delete that database volume.

The backend reads settings from `backend/.env` and otherwise uses local development defaults. Keep `.env` files and real credentials out of Git. The frontend uses `NEXT_PUBLIC_API_URL`, defaulting to `http://localhost:8000`.

To display the optional proposal examples, explicitly enable the setting in both applications before starting them:

```text
# backend/.env
ENABLE_PARTNER_PROGRAMMES=true
```

```text
# frontend/.env.local
NEXT_PUBLIC_ENABLE_PARTNER_PROGRAMMES=true
```

Restart both servers after changing these settings. Leave them unset for the independent default product experience.

## Tests and build

From the project root:

```powershell
python -m pytest backend/tests/ -v
python -m pytest ai/tests/ -v
```

For a frontend production build:

```powershell
cd frontend
npm run build
```

## Demo and technical notes

- [Demo guide](docs/DEMO_GUIDE.md) — local setup, the shared walkthrough, and two competition-specific presentation paths.
- [Demo script](docs/DEMO_SCRIPT.md) — concise narration for the shared product flow.
- [Known limitations](docs/KNOWN_LIMITATIONS.md)
- [API contracts](docs/API_CONTRACTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data model](docs/DATA_MODEL.md)
- [Licence and attribution](docs/LICENCE_AND_ATTRIBUTION.md)
