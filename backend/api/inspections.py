"""GripWise Backend — Inspections router with full workflow."""
import hashlib
import os
import time
import uuid
import structlog
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import User, Vehicle, TyrePosition, Inspection, InspectionObservation, AuditEvent
from backend.schemas import ApiResponse
from backend.auth import get_current_user
from backend.config import settings

log = structlog.get_logger()
router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024


def _observation_out(obs: InspectionObservation) -> dict:
    value = obs.value_numeric if obs.value_numeric is not None else (
        obs.value_bool if obs.value_bool is not None else obs.value_text
    )
    return {
        "field": obs.field_name,
        "value": value,
        "confidence": obs.confidence_tier,
        "explanation": obs.explanation,
        "caveat": obs.caveat,
    }


def _inspection_out(insp: Inspection, mechanic_verified: bool = False) -> dict:
    return {
        "inspection_id": insp.id,
        "tyre_position_id": insp.tyre_position_id,
        "status": insp.status,
        "created_at": insp.created_at.isoformat(),
        "completed_at": insp.completed_at.isoformat() if insp.completed_at else None,
        "inference_provider": insp.inference_provider,
        "model_version": insp.model_version,
        "image_quality": {
            "status": insp.image_quality_status,
            "issues": insp.quality_issues or [],
        },
        "recommended_action": insp.recommended_action,
        "recommended_action_explanation": insp.recommended_action_explanation,
        "observations": [_observation_out(o) for o in (insp.observations or [])],
        "inference_ms": insp.inference_ms,
        "mechanic_verified": mechanic_verified,
    }


async def _run_inference(inspection_id: str):
    """Background task: run AI inference and update inspection record."""
    from backend.database import AsyncSessionLocal
    from ai.factory import get_provider

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Inspection).where(Inspection.id == inspection_id)
                .options(selectinload(Inspection.observations))
            )
            insp = result.scalar_one_or_none()
            if not insp:
                return

            insp.status = "PROCESSING"
            await db.flush()

            # Load image bytes
            image_path = Path(insp.image_path)
            if not image_path.exists():
                insp.status = "FAILED"
                await db.commit()
                return

            image_bytes = image_path.read_bytes()
            provider = get_provider()
            ai_result = provider.analyse(image_bytes)

            # Update inspection
            insp.status = "COMPLETE"
            insp.inference_provider = ai_result.provider
            insp.model_version = ai_result.model_version
            insp.image_quality_status = ai_result.image_quality
            insp.quality_issues = ai_result.quality_issues
            insp.recommended_action = ai_result.recommended_action.value
            insp.recommended_action_explanation = ai_result.recommended_action_explanation
            insp.inference_ms = ai_result.inference_ms
            insp.completed_at = datetime.now(timezone.utc)

            # Save observations
            for obs in ai_result.observations:
                value_numeric = obs.value if isinstance(obs.value, (int, float)) and not isinstance(obs.value, bool) else None
                value_bool = obs.value if isinstance(obs.value, bool) else None
                value_text = str(obs.value) if obs.value is not None and value_numeric is None and value_bool is None else None

                db_obs = InspectionObservation(
                    inspection_id=inspection_id,
                    field_name=obs.field,
                    value_numeric=value_numeric,
                    value_bool=value_bool,
                    value_text=value_text,
                    confidence_tier=obs.confidence.value,
                    explanation=obs.explanation,
                    caveat=obs.caveat,
                )
                db.add(db_obs)

            await db.commit()
            log.info("inspection.completed", inspection_id=inspection_id, provider=ai_result.provider)
        except Exception as e:
            log.error("inspection.inference_failed", inspection_id=inspection_id, error=str(e))
            try:
                insp.status = "FAILED"
                await db.commit()
            except Exception:
                pass


@router.post("", status_code=202)
async def submit_inspection(
    background_tasks: BackgroundTasks,
    tyre_position_id: str = Form(...),
    odometer_km: int | None = Form(None),
    notes: str | None = Form(None),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate content type
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, detail={"code": "IMAGE_INVALID_TYPE", "message": f"Unsupported image type: {image.content_type}. Use JPEG, PNG, or WEBP."})

    image_bytes = await image.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(413, detail={"code": "IMAGE_TOO_LARGE", "message": f"Image exceeds {settings.MAX_IMAGE_SIZE_MB} MB limit."})

    # Validate ownership of tyre position
    result = await db.execute(
        select(TyrePosition)
        .join(Vehicle, Vehicle.id == TyrePosition.vehicle_id)
        .where(TyrePosition.id == tyre_position_id, Vehicle.owner_id == current_user.id, Vehicle.deleted_at == None)
    )
    tp = result.scalar_one_or_none()
    if not tp:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Tyre position not found or not owned by you."})

    # Store image
    img_hash = hashlib.sha256(image_bytes).hexdigest()
    upload_dir = Path(settings.IMAGE_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = "jpg" if image.content_type == "image/jpeg" else image.content_type.split("/")[-1]
    filename = f"{img_hash}.{ext}"
    img_path = upload_dir / filename
    if not img_path.exists():
        img_path.write_bytes(image_bytes)

    # Create inspection record
    insp = Inspection(
        tyre_position_id=tyre_position_id,
        submitted_by=current_user.id,
        odometer_km=odometer_km,
        image_path=str(img_path),
        image_hash=img_hash,
        image_size_bytes=len(image_bytes),
        image_quality_status="UNKNOWN",
        status="PENDING",
        notes=notes,
    )
    db.add(insp)
    await db.flush()
    await db.refresh(insp)

    # Audit event
    db.add(AuditEvent(
        actor_id=current_user.id,
        actor_role=current_user.role,
        event_type="inspection.created",
        resource_type="inspection",
        resource_id=insp.id,
        detail={"tyre_position_id": tyre_position_id},
    ))
    await db.commit()

    background_tasks.add_task(_run_inference, insp.id)
    log.info("inspection.submitted", inspection_id=insp.id, user_id=current_user.id)

    return ApiResponse.ok({
        "inspection_id": insp.id,
        "status": "PENDING",
        "poll_url": f"/api/inspections/{insp.id}",
    })


@router.get("/{inspection_id}")
async def get_inspection(
    inspection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from backend.models import MechanicFinding
    result = await db.execute(
        select(Inspection)
        .where(Inspection.id == inspection_id, Inspection.submitted_by == current_user.id)
        .options(selectinload(Inspection.observations))
    )
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Inspection not found."})
        
    finding_res = await db.execute(select(MechanicFinding.id).where(MechanicFinding.inspection_id == inspection_id))
    has_finding = finding_res.first() is not None

    return ApiResponse.ok(_inspection_out(insp, mechanic_verified=has_finding))


@router.get("")
async def list_inspections(
    tyre_position_id: str | None = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Inspection)
        .where(Inspection.submitted_by == current_user.id)
        .options(selectinload(Inspection.observations))
        .order_by(Inspection.created_at.desc())
        .limit(min(limit, 100))
    )
    if tyre_position_id:
        query = query.where(Inspection.tyre_position_id == tyre_position_id)

    result = await db.execute(query)
    inspections = result.scalars().all()
    return ApiResponse.ok({"inspections": [_inspection_out(i) for i in inspections]})


@router.get("/{inspection_id}/image")
async def get_image(
    inspection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Inspection).where(Inspection.id == inspection_id, Inspection.submitted_by == current_user.id)
    )
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Inspection not found."})
    img_path = Path(insp.image_path)
    if not img_path.exists():
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Image file not found."})
    return FileResponse(str(img_path))
