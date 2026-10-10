# GripWise — Data Model

**Status:** PLANNED — not yet implemented
**Date:** 2026-10-10
**Database:** PostgreSQL 16

All tables use UUID primary keys, UTC timestamps, and soft-delete where appropriate.
All schema changes managed via Alembic migrations.

---

## 1. Entity Relationship Overview

```
users ──────────────────────────────────────────┐
  │                                             │
  ├── vehicles ──── tyre_positions              │ (mechanic access)
  │       │               │                    │
  │       │          inspections ────── inspection_observations
  │       │               │
  │       │          mechanic_findings (mechanic FK → users)
  │       │               │
  │       │          service_records (mechanic FK → users)
  │       │
  │       └── maintenance_reminders
  │                   │
  │               reminder_rules (system-defined)
  │
  ├── consent_records (rider FK, mechanic FK, inspection FK)
  ├── audit_events
  └── analytics_events
```

---

## 2. Table Definitions

### 2.1 users

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE,
    mobile          VARCHAR(20) UNIQUE,
    display_name    VARCHAR(100) NOT NULL,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('RIDER','MECHANIC','ADMIN')),
    workshop_name   VARCHAR(200),        -- mechanics only
    workshop_city   VARCHAR(100),        -- mechanics only
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ          -- soft delete
);
CREATE INDEX idx_users_role ON users(role);
```

**Notes:**
- Either `email` or `mobile` must be non-null (enforced at application layer)
- `workshop_name` / `workshop_city` relevant only for MECHANIC role
- Passwords stored as bcrypt hash in separate `user_credentials` table (not shown; separation of concerns)

---

### 2.2 vehicles

```sql
CREATE TABLE vehicles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID NOT NULL REFERENCES users(id),
    make            VARCHAR(100) NOT NULL,
    model           VARCHAR(100) NOT NULL,
    year            SMALLINT,
    registration    VARCHAR(20),
    vehicle_type    VARCHAR(20) NOT NULL DEFAULT 'MOTORCYCLE'
                    CHECK (vehicle_type IN ('MOTORCYCLE','SCOOTER','BICYCLE','OTHER')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_vehicles_owner ON vehicles(owner_id);
```

---

### 2.3 tyre_positions

```sql
CREATE TABLE tyre_positions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id      UUID NOT NULL REFERENCES vehicles(id),
    position        VARCHAR(20) NOT NULL
                    CHECK (position IN ('FRONT','REAR','FRONT_LEFT','FRONT_RIGHT','REAR_LEFT','REAR_RIGHT')),
    brand           VARCHAR(100),
    model_name      VARCHAR(100),
    size_spec       VARCHAR(50),           -- e.g. "90/90-17"
    installed_at    DATE,
    installed_km    INTEGER,               -- odometer at installation
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (vehicle_id, position)
);
```

---

### 2.4 inspections

```sql
CREATE TABLE inspections (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tyre_position_id    UUID NOT NULL REFERENCES tyre_positions(id),
    submitted_by        UUID NOT NULL REFERENCES users(id),
    odometer_km         INTEGER,
    image_path          VARCHAR(500) NOT NULL,
    image_hash          CHAR(64) NOT NULL,          -- SHA-256 hex
    image_size_bytes    INTEGER NOT NULL,
    image_quality_status VARCHAR(20) NOT NULL
                        CHECK (image_quality_status IN ('PASS','DEGRADED','FAIL')),
    quality_issues      TEXT[],                      -- array of issue codes
    inference_provider  VARCHAR(50) NOT NULL,        -- "mock" | "cv_pipeline"
    model_version       VARCHAR(50) NOT NULL,        -- semver of ai/ package
    recommended_action  VARCHAR(50)
                        CHECK (recommended_action IN (
                          'ok','monitor','inspect_soon','replace_urgently','seek_mechanic_now','analysis_failed'
                        )),
    inference_ms        REAL,
    status              VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING','COMPLETE','FAILED','MECHANIC_REVIEWED')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at        TIMESTAMPTZ,
    notes               TEXT
);
CREATE INDEX idx_inspections_tyre ON inspections(tyre_position_id);
CREATE INDEX idx_inspections_submitted_by ON inspections(submitted_by);
CREATE INDEX idx_inspections_created ON inspections(created_at DESC);
```

---

### 2.5 inspection_observations

One row per observation field per inspection. Allows independent confidence tiers and future schema extension without migrations.

```sql
CREATE TABLE inspection_observations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inspection_id   UUID NOT NULL REFERENCES inspections(id),
    field_name      VARCHAR(100) NOT NULL,   -- e.g. "tread_score", "anomaly_detected"
    value_numeric   REAL,
    value_text      VARCHAR(200),
    value_bool      BOOLEAN,
    confidence_tier VARCHAR(30) NOT NULL
                    CHECK (confidence_tier IN (
                      'HIGH_CONFIDENCE','MEDIUM_CONFIDENCE','LOW_CONFIDENCE','NOT_AVAILABLE'
                    )),
    explanation     TEXT NOT NULL,           -- human-readable reason
    caveat          TEXT,                    -- mandatory uncertainty disclosure for certain fields
    raw_payload     JSONB,                   -- full sub-module output for debugging
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (inspection_id, field_name)
);

-- Standard field_name values (not enforced by DB; enforced by application):
-- tread_score         (0-100 relative indicator)
-- wear_percentage     (0-100)
-- groove_count        (integer)
-- anomaly_detected    (bool)
-- anomaly_confidence  (0-1)
-- condition_class     (Good/Worn/Critical — only when CNN available)
-- detected_tyres      (count)
-- image_brightness    (0-255)
-- image_blur_var      (Laplacian variance)
```

---

### 2.6 mechanic_findings

Mechanic's physical verification; stored separately from AI observations.

```sql
CREATE TABLE mechanic_findings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inspection_id   UUID NOT NULL REFERENCES inspections(id),
    mechanic_id     UUID NOT NULL REFERENCES users(id),
    field_name      VARCHAR(100) NOT NULL,
    physical_value  VARCHAR(500),            -- free text or structured value
    verified        BOOLEAN NOT NULL,
    verification_note TEXT,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (inspection_id, mechanic_id, field_name)
);
```

---

### 2.7 service_records

```sql
CREATE TABLE service_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inspection_id   UUID REFERENCES inspections(id),
    tyre_position_id UUID NOT NULL REFERENCES tyre_positions(id),
    mechanic_id     UUID NOT NULL REFERENCES users(id),
    service_type    VARCHAR(50) NOT NULL
                    CHECK (service_type IN (
                      'INFLATION_ADJUSTMENT','ROTATION','REPLACEMENT',
                      'PUNCTURE_REPAIR','BALANCE','OTHER'
                    )),
    new_tyre_brand  VARCHAR(100),
    new_tyre_model  VARCHAR(100),
    new_tyre_size   VARCHAR(50),
    odometer_km     INTEGER,
    labour_notes    VARCHAR(500),
    serviced_at     DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

### 2.8 reminder_rules

System-defined, human-readable maintenance rules.

```sql
CREATE TABLE reminder_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name       VARCHAR(200) NOT NULL UNIQUE,
    description     TEXT NOT NULL,           -- shown to rider
    trigger_field   VARCHAR(100) NOT NULL,   -- inspection_observations.field_name
    trigger_op      VARCHAR(10) NOT NULL,    -- '<', '>', '=', 'consecutive_below'
    trigger_value   REAL NOT NULL,
    trigger_count   SMALLINT DEFAULT 1,      -- how many consecutive inspections
    action_message  TEXT NOT NULL,
    urgency         VARCHAR(20) NOT NULL CHECK (urgency IN ('INFO','CAUTION','URGENT')),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    version         SMALLINT NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Example seed data:
```sql
INSERT INTO reminder_rules (rule_name, description, trigger_field, trigger_op, trigger_value, trigger_count, action_message, urgency) VALUES
('low_tread_single',
 'Tread wear indicator below moderate threshold on one inspection',
 'tread_score', '<', 40, 1,
 'Tread wear indicator is moderate. Consider scheduling a tyre inspection with a mechanic within the next 30 days.',
 'CAUTION'),
('low_tread_consecutive',
 'Tread wear indicator below threshold on two consecutive inspections',
 'tread_score', '<', 40, 2,
 'Tread wear indicator has been moderate or below for two consecutive inspections. We recommend scheduling a professional inspection soon.',
 'URGENT'),
('anomaly_detected',
 'Tyre anomaly detected in inspection',
 'anomaly_detected', '=', 1, 1,
 'An anomaly was detected in your tyre image. This does not confirm a puncture but warrants a physical check by a mechanic.',
 'URGENT');
```

---

### 2.9 maintenance_reminders

```sql
CREATE TABLE maintenance_reminders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id        UUID NOT NULL REFERENCES users(id),
    tyre_position_id UUID NOT NULL REFERENCES tyre_positions(id),
    rule_id         UUID NOT NULL REFERENCES reminder_rules(id),
    trigger_inspection_id UUID REFERENCES inspections(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING','ACTIONED','DISMISSED','EXPIRED')),
    dismissed_reason VARCHAR(500),
    actioned_at     TIMESTAMPTZ,
    dismissed_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_reminders_rider ON maintenance_reminders(rider_id, status);
```

---

### 2.10 consent_records

```sql
CREATE TABLE consent_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id        UUID NOT NULL REFERENCES users(id),
    mechanic_id     UUID NOT NULL REFERENCES users(id),
    inspection_id   UUID NOT NULL REFERENCES inspections(id),
    granted         BOOLEAN NOT NULL,
    granted_at      TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX idx_consent_unique ON consent_records(rider_id, mechanic_id, inspection_id);
```

---

### 2.11 audit_events

```sql
CREATE TABLE audit_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id        UUID REFERENCES users(id),   -- NULL for system events
    actor_role      VARCHAR(20),
    event_type      VARCHAR(100) NOT NULL,       -- e.g. "inspection.created", "consent.granted"
    resource_type   VARCHAR(50),
    resource_id     UUID,
    detail          JSONB,
    ip_address      INET,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_resource ON audit_events(resource_type, resource_id);
CREATE INDEX idx_audit_occurred ON audit_events(occurred_at DESC);
```

---

### 2.12 analytics_events

Separate from audit_events; used for engagement analytics only.

```sql
CREATE TABLE analytics_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name      VARCHAR(100) NOT NULL,
    user_id         UUID,                        -- pseudonymous; may be NULL
    vehicle_id      UUID,
    properties      JSONB,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_analytics_event ON analytics_events(event_name, occurred_at DESC);
```

Standard event names:
- `inspection.submitted`, `inspection.completed`, `inspection.failed_quality`
- `mechanic.finding_recorded`, `mechanic.service_completed`
- `reminder.triggered`, `reminder.actioned`, `reminder.dismissed`
- `session.rider_login`, `session.mechanic_login`

---

## 3. Key Design Decisions

| Decision | Rationale |
|---|---|
| UUID primary keys | Avoids sequential ID enumeration attacks; safe for future distributed deployment |
| `inspection_observations` as separate table | Allows per-field confidence tiers; avoids wide nullable columns; supports future fields without schema migration |
| `mechanic_findings` separate from `inspection_observations` | Preserves provenance: AI and human findings never mixed in same record |
| `reminder_rules` as database rows | Rules are visible and auditable by admins; can be updated without code deploys |
| Soft delete on `users` and `vehicles` | GDPR/DPDPA-style right-to-erasure requires records to be markable as deleted without cascade data loss |
| `image_hash` (SHA-256) on `inspections` | Content-addressing for deduplication; hash stored for tamper-detection |
| `inference_provider` and `model_version` on `inspections` | Historical inspections interpretable even after model upgrades |
| JSONB `raw_payload` on observations | Preserves full sub-module output for debugging; not shown to rider directly |
