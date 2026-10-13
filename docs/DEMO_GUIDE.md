# GripWise Demo Guide

GripWise is one independent product with two presentation paths. Use the same rider-to-workshop workflow for both; change the story you tell, not the product setup.

## Start the application locally

Prerequisites: Python 3.13, Node.js/npm, and Docker Desktop. Run these commands from the project root in three terminals.

**Terminal 1 — PostgreSQL:**

```powershell
docker compose up -d db
```

**Terminal 2 — FastAPI:**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 3 — Next.js:**

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>. API documentation: <http://localhost:8000/api/docs>. The backend uses `backend/.env` when present; its database URL must point to the locally published PostgreSQL port (`localhost:5432`) when FastAPI runs on the host. The frontend defaults to `http://localhost:8000` for the API. Keep `.env` files private and do not paste their contents into a demo or commit them.

The core app does not require the optional Partner Programmes section. To show its proposal-only examples, set both `ENABLE_PARTNER_PROGRAMMES=true` in `backend/.env` and `NEXT_PUBLIC_ENABLE_PARTNER_PROGRAMMES=true` in `frontend/.env.local`, then restart both servers. This is only a local display/configuration switch; it does not activate a real offer, sponsor, partnership, or accreditation.

## Shared product walkthrough

1. Create or sign in to a rider account and add a vehicle. Use demonstration accounts and images that you are permitted to use; do not enter real customer data into a public demo.
2. Submit an inspection image and open the report. The repository defaults to the `mock` provider. Say plainly that the displayed result is simulated and does not analyze the image or measure tread depth. The interface also labels mock output.
3. Create or sign in to a mechanic account. On **Service Queue**, copy the full **Workshop ID**. It is a UUID generated for that mechanic account; there is no numeric mechanic ID to configure in `.env`.
4. Return to the rider account, open **Mechanic Access**, paste the full Workshop ID, and grant access. The mechanic’s queue should then show the authorized inspection. Access can be revoked from the same rider page.
5. In the mechanic account, open the inspection and demonstrate the findings and service record workflow. Save physical measurements only if they were actually taken for the demo.
6. Open **Mechanic Growth**. Show the profile completion checklist and learning modules. Enter only accurate profile information. Recognition is based on recorded GripWise activity and is not an independent professional certification.
7. Customer follow-ups require the customer’s agreement. The consent checkbox starts unchecked. For a demonstration, use a clearly labelled demo record, avoid real contact details, and do not describe demo activity as real customer activity.
8. If applicable, return to the rider and revoke the mechanic’s access. The mechanic should no longer be able to retrieve that inspection.

The mechanic must share their Workshop ID with the rider first. The rider grants access; mechanics cannot grant themselves access to rider records.

## Tata Imagination Challenge presentation path

Emphasize the rider’s preventive-maintenance journey:

- Keeping vehicle, inspection, and service records together.
- Showing recommendations in plain language and encouraging a physical inspection where needed.
- Letting riders decide which workshop can view an inspection and revoke that permission.
- Describing the prototype’s current image analysis honestly. Do not claim accident reduction, validated AI accuracy, or a millimetre tread-depth result from mock output.

## Eurogrip TORQ Challenge 4.0 presentation path

Use the same core walkthrough, then emphasize the mechanic’s professional workflow:

- Accurate workshop profile completion and tyre-care learning.
- Quiz progress and recognition tied to recorded activity.
- Consent-aware follow-ups and clear rider control over inspection access.
- Optional Partner Programmes only if you deliberately enabled the configuration. Describe those cards as proposed concepts; do not imply approval, sponsorship, funding, a partnership, accreditation, or an active offer.

The default product screens are competition-neutral. The competition names belong in the presentation narrative and are not shown in the default application UI.

## Limitations to disclose

- The default `mock` inspection provider returns simulated results; no real image analysis is performed in that mode.
- The app does not provide calibrated tread-depth measurements, validated safety classifications, or a replacement for a qualified physical inspection.
- Local uploads and the configured database are development/demo storage, not a production deployment.
- Learning badges represent in-app activity, not third-party certification.
- Partner Programme cards are conceptual examples only and are disabled by default.
