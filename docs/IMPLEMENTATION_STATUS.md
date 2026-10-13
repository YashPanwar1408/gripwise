# GripWise Implementation Status

## Core rider and workshop workflows

- Rider registration, vehicle records, inspection uploads, reports, and service history are implemented.
- Riders grant and revoke mechanic access through the consent workflow.
- Mechanics see only inspections authorized for their Workshop ID, and can add physical findings and service records.
- The inspection provider defaults to `mock`; simulated output is identified in the interface.

## Mechanic Growth

The mechanic profile, completion checklist, learning modules, quizzes, activity recognition, and consent-aware customer follow-ups reuse the existing tables and API routes. For compatibility, the frontend path remains `/mechanic/saathi` and the backend namespace remains `/api/saathi`; the user-facing label is **Mechanic Growth**.

Profile completion recognition is labelled as a completion marker and does not verify a workshop. Learning and activity badges are not third-party certifications. Seeded learning and badge copy is refreshed by stable IDs; completion, earned-badge, referral, and service records are preserved.

## Optional Partner Programmes

Proposal examples are hidden by default. The backend endpoint returns an empty list unless `ENABLE_PARTNER_PROGRAMMES=true`; the frontend tab and request are also disabled unless `NEXT_PUBLIC_ENABLE_PARTNER_PROGRAMMES=true`. Enabling both switches only exposes conceptual examples and does not create an approved offer or partnership.

## Database and migrations

The existing profile, learning, recognition, referral, and initiative tables remain in place. Migration `001_mechanic_core.py` creates the rider-consent, mechanic-findings, and service-record tables required before `002_saathi_engagement.py`; it does not rewrite existing rows. The Saathi migration now depends on that core-workshop revision so the referral foreign key targets a table created earlier in the chain.

## Validation

Current workspace checks: 44 backend and AI tests passed; the Next.js production build passed; the Alembic chain applied to a disposable PostgreSQL 16 database through `003_followup_consent_default`, and a second upgrade was clean. See [TEST_REPORT.md](TEST_REPORT.md) for the commands and scope.
