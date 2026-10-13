# GripWise — API Contracts

**Status:** PLANNED — not yet implemented
**Date:** 2026-10-10
**Base URL:** `http://localhost:8000/api` (local dev)
**Format:** JSON over HTTPS. All timestamps in ISO 8601 UTC.
**Auth:** Bearer JWT in `Authorization` header (except /auth/*)

---

## 1. Conventions

### 1.1 Standard Response Envelope

All endpoints return this envelope:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

On error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": { "field": "reason" }
  }
}
```

### 1.2 Error Codes

| Code | HTTP Status | Meaning |
|---|---|---|
| VALIDATION_ERROR | 422 | Request body or query param invalid |
| UNAUTHORIZED | 401 | Missing or invalid JWT |
| FORBIDDEN | 403 | Valid JWT but insufficient role |
| NOT_FOUND | 404 | Resource does not exist or not accessible to caller |
| IMAGE_TOO_LARGE | 413 | Uploaded image exceeds 10 MB |
| IMAGE_INVALID_TYPE | 415 | Not JPEG/PNG/WEBP |
| INFERENCE_UNAVAILABLE | 503 | AI provider failed to return result |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Unexpected server error (detail omitted) |

### 1.3 Confidence Tier Values

Used throughout inspection response bodies:
- `"HIGH_CONFIDENCE"` — algorithm has high certainty under good image conditions
- `"MEDIUM_CONFIDENCE"` — algorithm output likely but influenced by image quality
- `"LOW_CONFIDENCE"` — algorithm ran but conditions degraded; treat output as indicative only
- `"NOT_AVAILABLE"` — model weights absent or algorithm failed; field not computed

### 1.4 Pagination

List endpoints support cursor-based pagination:

```
GET /api/inspections?limit=20&cursor=<opaque_cursor>
```

Response includes `"next_cursor": "<value> | null"`.

---

## 2. Authentication Endpoints

### POST /api/auth/register

Register a new rider or mechanic account.

**Request:**
```json
{
  "display_name": "Rajan Kumar",
  "email": "rajan@example.com",
  "mobile": "+919876543210",
  "role": "RIDER",
  "password": "••••••••",
  "workshop_name": null,
  "workshop_city": null
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "role": "RIDER",
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

**Validation rules:**
- `role`: "RIDER" | "MECHANIC"
- `password`: min 8 chars
- Either `email` or `mobile` required; both accepted
- `workshop_name` required if `role == "MECHANIC"`

---

### POST /api/auth/login

**Request:**
```json
{ "credential": "rajan@example.com", "password": "••••••••" }
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "role": "RIDER",
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

---

### POST /api/auth/refresh

**Request:**
```json
{ "refresh_token": "eyJ..." }
```

**Response 200:** Same structure as login.

---

## 3. Vehicle Endpoints (RIDER role)

### POST /api/vehicles

Register a new vehicle.

**Request:**
```json
{
  "make": "Honda",
  "model": "Activa 6G",
  "year": 2022,
  "registration": "MH01AB1234",
  "vehicle_type": "SCOOTER"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "vehicle_id": "uuid",
    "make": "Honda",
    "model": "Activa 6G",
    "year": 2022,
    "registration": "MH01AB1234",
    "vehicle_type": "SCOOTER",
    "tyre_positions": [],
    "created_at": "2026-10-10T08:00:00Z"
  }
}
```

---

### GET /api/vehicles

List caller's vehicles.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "vehicles": [ { ...vehicle objects... } ]
  }
}
```

---

### POST /api/vehicles/{vehicle_id}/tyre-positions

Register a tyre position.

**Request:**
```json
{
  "position": "FRONT",
  "brand": "Example manufacturer",
  "model_name": "Example commuter tyre",
  "size_spec": "90/90-12",
  "installed_at": "2026-03-15",
  "installed_km": 14200
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "tyre_position_id": "uuid",
    "vehicle_id": "uuid",
    "position": "FRONT",
    "brand": "Example manufacturer",
    "model_name": "Example commuter tyre",
    "size_spec": "90/90-12",
    "installed_at": "2026-03-15",
    "installed_km": 14200
  }
}
```

---

## 4. Inspection Endpoints

### POST /api/inspections

Submit a tyre image for analysis.

**Request:** `multipart/form-data`

| Field | Type | Required | Notes |
|---|---|---|---|
| `image` | file | YES | JPEG/PNG/WEBP, max 10 MB |
| `tyre_position_id` | string (UUID) | YES | Must belong to caller |
| `odometer_km` | integer | NO | Current odometer reading |
| `notes` | string | NO | Max 500 chars |

**Response 202 (Accepted — analysis queued):**
```json
{
  "success": true,
  "data": {
    "inspection_id": "uuid",
    "status": "PENDING",
    "poll_url": "/api/inspections/uuid"
  }
}
```

**Error responses:**
- `413 IMAGE_TOO_LARGE`: file > 10 MB
- `415 IMAGE_INVALID_TYPE`: not JPEG/PNG/WEBP
- `404 NOT_FOUND`: tyre_position_id not found or not owned by caller

---

### GET /api/inspections/{inspection_id}

Retrieve inspection result. Poll until `status != "PENDING"`.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "inspection_id": "uuid",
    "tyre_position_id": "uuid",
    "status": "COMPLETE",
    "created_at": "2026-10-10T08:01:00Z",
    "completed_at": "2026-10-10T08:01:04Z",
    "inference_provider": "cv_pipeline",
    "model_version": "0.1.0",
    "image_quality": {
      "status": "PASS",
      "issues": []
    },
    "recommended_action": "monitor",
    "recommended_action_explanation": "Tread wear indicator is moderate. Physical inspection recommended within 30 days.",
    "observations": [
      {
        "field": "tread_score",
        "value": 42.3,
        "confidence": "MEDIUM_CONFIDENCE",
        "explanation": "Edge density and groove transitions indicate moderate wear.",
        "caveat": "This is a relative wear indicator derived from image pixel analysis. It is not a tread depth measurement in mm and has not been calibrated against physical measurements."
      },
      {
        "field": "anomaly_detected",
        "value": false,
        "confidence": "LOW_CONFIDENCE",
        "explanation": "No anomalous dark contours detected above threshold.",
        "caveat": "Anomaly detection may miss defects not visible on tyre surface or in poor lighting."
      },
      {
        "field": "condition_class",
        "value": null,
        "confidence": "NOT_AVAILABLE",
        "explanation": "Condition classifier model weights are not available in this deployment.",
        "caveat": null
      }
    ],
    "mechanic_findings": [],
    "service_records": [],
    "inference_ms": 842.3
  }
}
```

**Access rules:**
- Rider: can access own inspections only
- Mechanic: can access inspections where an active consent_record exists
- Admin: can access all inspections

---

### GET /api/inspections

List inspections for the calling rider.

**Query params:** `tyre_position_id`, `limit` (default 20), `cursor`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "inspections": [ { ...summary objects... } ],
    "next_cursor": "opaque_cursor | null"
  }
}
```

---

## 5. Mechanic Endpoints (MECHANIC role)

### POST /api/mechanic/findings

Record a physical finding for an inspection.

**Request:**
```json
{
  "inspection_id": "uuid",
  "findings": [
    {
      "field_name": "tread_score",
      "physical_value": "Tread is visibly worn; approximately 2mm remaining",
      "verified": true,
      "verification_note": "Measured with tread depth gauge"
    },
    {
      "field_name": "anomaly_detected",
      "physical_value": "No puncture found; small nail visible but seated",
      "verified": true,
      "verification_note": null
    }
  ]
}
```

**Validation:**
- `inspection_id` must have an active consent_record for this mechanic
- `verified`: true = physically confirmed; false = could not verify

**Response 201:**
```json
{
  "success": true,
  "data": {
    "findings_recorded": 2,
    "inspection_id": "uuid",
    "mechanic_id": "uuid"
  }
}
```

---

### POST /api/mechanic/service-records

Record a service action.

**Request:**
```json
{
  "tyre_position_id": "uuid",
  "inspection_id": "uuid",
  "service_type": "INFLATION_ADJUSTMENT",
  "odometer_km": 21400,
  "labour_notes": "Inflated to 32 PSI. Front tyre. Valve cap replaced.",
  "serviced_at": "2026-10-10"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": { "service_record_id": "uuid" }
}
```

---

## 6. Consent Endpoints (RIDER role)

### POST /api/consent

Grant mechanic access to an inspection.

**Request:**
```json
{
  "mechanic_id": "uuid",
  "inspection_id": "uuid"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": { "consent_id": "uuid", "granted": true }
}
```

---

### DELETE /api/consent/{consent_id}

Revoke mechanic access.

**Response 200:**
```json
{
  "success": true,
  "data": { "revoked_at": "2026-10-10T09:00:00Z" }
}
```

---

## 7. Maintenance Reminder Endpoints

### GET /api/reminders

List active reminders for the calling rider.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "reminders": [
      {
        "reminder_id": "uuid",
        "tyre_position": { "vehicle": "Honda Activa 6G", "position": "FRONT" },
        "rule_name": "low_tread_single",
        "rule_description": "Tread wear indicator below moderate threshold on one inspection",
        "action_message": "Tread wear indicator is moderate. Consider scheduling a tyre inspection with a mechanic within the next 30 days.",
        "urgency": "CAUTION",
        "triggered_by_inspection": "uuid",
        "status": "PENDING",
        "created_at": "2026-10-10T08:01:05Z"
      }
    ]
  }
}
```

---

### PATCH /api/reminders/{reminder_id}

Update reminder status.

**Request:**
```json
{
  "status": "DISMISSED",
  "dismissed_reason": "Will check with mechanic this weekend"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": { "reminder_id": "uuid", "status": "DISMISSED" }
}
```

---

## 8. Analytics Endpoints (ADMIN role)

### GET /api/analytics/overview

**Response 200:**
```json
{
  "success": true,
  "data": {
    "period": "last_30_days",
    "total_inspections": 412,
    "inspections_passed_quality": 389,
    "inspections_with_mechanic_review": 87,
    "mechanic_participation_rate": 0.224,
    "active_riders": 143,
    "active_mechanics": 12,
    "reminders_triggered": 56,
    "reminders_actioned": 23,
    "reminders_dismissed": 19,
    "repeat_inspection_rate": 0.61
  }
}
```

---

## 9. AI Health Endpoint (Internal)

### GET /api/ai/health

**Response 200:**
```json
{
  "success": true,
  "data": {
    "provider": "cv_pipeline",
    "model_version": "0.1.0",
    "detection_available": true,
    "tread_analysis_available": true,
    "anomaly_detection_available": true,
    "condition_classifier_available": false,
    "classifier_note": "CNN weights not present. Observation will return NOT_AVAILABLE."
  }
}
```

---

## 10. Error Handling Design

### Image Quality Failure Example

When image quality check fails, the inspection status is set to `FAILED` and the response includes structured guidance:

```json
{
  "success": true,
  "data": {
    "inspection_id": "uuid",
    "status": "FAILED",
    "image_quality": {
      "status": "FAIL",
      "issues": ["BLUR_DETECTED", "TYRE_NOT_FOUND"]
    },
    "quality_guidance": {
      "BLUR_DETECTED": "Hold the camera steady. Use tap-to-focus. Ensure adequate lighting.",
      "TYRE_NOT_FOUND": "Position the tyre to fill most of the frame. Shoot at 90 degrees to the tyre surface."
    },
    "observations": [],
    "recommended_action": "analysis_failed"
  }
}
```

### Inference Unavailable Example

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INFERENCE_UNAVAILABLE",
    "message": "The AI analysis service encountered an error. Your image has been saved. Please try again or contact support.",
    "details": {
      "inspection_id": "uuid",
      "provider": "cv_pipeline"
    }
  }
}
```

---

## 11. Security Notes

- All endpoints require valid JWT except `/api/auth/*`
- `tyre_position_id` in POST /api/inspections validated against calling user's vehicles
- `inspection_id` in POST /api/mechanic/findings validated against consent_records
- `inspection_id` in GET /api/inspections/{id} validated against caller ownership or active consent
- Image files served only through `/api/inspections/{id}/image` (authenticated), never as static files
- Rate limiting: 10 image submissions per rider per hour (configurable)
