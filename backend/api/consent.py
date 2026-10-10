"""GripWise Backend — Consent records router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import structlog

from backend.database import get_db
from backend.models import User, ConsentRecord, AuditEvent
from backend.schemas import ApiResponse, ConsentRecordCreate, ConsentRecordOut
from backend.auth import get_current_user

log = structlog.get_logger()
router = APIRouter()


@router.post("", status_code=201)
async def grant_consent(
    req: ConsentRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "RIDER":
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "Only riders can grant consent."})

    # Verify mechanic exists
    mechanic = await db.get(User, req.mechanic_id)
    if not mechanic or mechanic.role != "MECHANIC":
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Mechanic not found."})

    # Check existing consent
    result = await db.execute(
        select(ConsentRecord)
        .where(ConsentRecord.rider_id == current_user.id, ConsentRecord.mechanic_id == req.mechanic_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.revoked_at = None # Reactivate if previously revoked
        consent = existing
    else:
        consent = ConsentRecord(rider_id=current_user.id, mechanic_id=req.mechanic_id)
        db.add(consent)

    await db.flush()
    
    # Audit event
    db.add(AuditEvent(
        actor_id=current_user.id,
        actor_role=current_user.role,
        event_type="consent.granted",
        resource_type="consent_record",
        resource_id=consent.id,
        detail={"mechanic_id": req.mechanic_id}
    ))
    await db.commit()

    return ApiResponse.ok({
        "id": consent.id,
        "rider_id": consent.rider_id,
        "mechanic_id": consent.mechanic_id,
        "granted_at": consent.granted_at.isoformat(),
        "revoked_at": None,
        "mechanic_name": mechanic.display_name,
        "workshop_name": mechanic.workshop_name
    })


@router.get("")
async def list_consents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == "RIDER":
        query = select(ConsentRecord, User).join(User, User.id == ConsentRecord.mechanic_id).where(ConsentRecord.rider_id == current_user.id)
    elif current_user.role == "MECHANIC":
        query = select(ConsentRecord, User).join(User, User.id == ConsentRecord.rider_id).where(ConsentRecord.mechanic_id == current_user.id)
    else:
        return ApiResponse.ok([])

    result = await db.execute(query)
    rows = result.all()
    
    consents = []
    for cr, user in rows:
        consents.append({
            "id": cr.id,
            "rider_id": cr.rider_id,
            "mechanic_id": cr.mechanic_id,
            "granted_at": cr.granted_at.isoformat(),
            "revoked_at": cr.revoked_at.isoformat() if cr.revoked_at else None,
            "mechanic_name": user.display_name if current_user.role == "RIDER" else None,
            "workshop_name": user.workshop_name if current_user.role == "RIDER" else None,
            "rider_name": user.display_name if current_user.role == "MECHANIC" else None
        })

    return ApiResponse.ok(consents)


@router.delete("/{consent_id}")
async def revoke_consent(
    consent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "RIDER":
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "Only riders can revoke consent."})

    consent = await db.get(ConsentRecord, consent_id)
    if not consent or consent.rider_id != current_user.id:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Consent record not found."})

    consent.revoked_at = datetime.now(timezone.utc)
    
    db.add(AuditEvent(
        actor_id=current_user.id,
        actor_role=current_user.role,
        event_type="consent.revoked",
        resource_type="consent_record",
        resource_id=consent.id,
    ))
    
    await db.commit()
    return ApiResponse.ok({"success": True})
