"""GripWise Backend — Mechanic API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import structlog

from backend.database import get_db
from backend.models import User, Inspection, ConsentRecord, MechanicFinding, ServiceRecord, AuditEvent, TyrePosition, Vehicle
from backend.schemas import ApiResponse, MechanicFindingCreate, ServiceRecordCreate
from backend.auth import get_current_user

log = structlog.get_logger()
router = APIRouter()

async def require_mechanic(user: User = Depends(get_current_user)):
    if user.role != "MECHANIC":
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "Mechanic role required."})
    return user


@router.get("/inspections")
async def list_consented_inspections(
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    # Get all rider IDs who have granted consent to this mechanic (and not revoked)
    consent_query = select(ConsentRecord.rider_id).where(
        ConsentRecord.mechanic_id == current_user.id,
        ConsentRecord.revoked_at == None
    )
    result = await db.execute(consent_query)
    rider_ids = result.scalars().all()

    if not rider_ids:
        return ApiResponse.ok({"inspections": []})

    # Fetch inspections for those riders
    query = (
        select(Inspection)
        .where(Inspection.submitted_by.in_(rider_ids))
        .options(selectinload(Inspection.observations), selectinload(Inspection.mechanic_findings))
        .order_by(Inspection.created_at.desc())
        .limit(100)
    )
    result = await db.execute(query)
    inspections = result.scalars().all()
    
    out = []
    for insp in inspections:
        out.append({
            "inspection_id": insp.id,
            "tyre_position_id": insp.tyre_position_id,
            "status": insp.status,
            "created_at": insp.created_at.isoformat(),
            "rider_id": insp.submitted_by,
            "has_mechanic_findings": len(insp.mechanic_findings) > 0
        })

    return ApiResponse.ok({"inspections": out})


@router.get("/inspections/{inspection_id}")
async def get_consented_inspection(
    inspection_id: str,
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    from backend.api.inspections import _inspection_out
    result = await db.execute(
        select(Inspection)
        .where(Inspection.id == inspection_id)
        .options(selectinload(Inspection.observations))
    )
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Inspection not found."})

    consent_res = await db.execute(
        select(ConsentRecord).where(
            ConsentRecord.mechanic_id == current_user.id,
            ConsentRecord.rider_id == insp.submitted_by,
            ConsentRecord.revoked_at == None
        )
    )
    if not consent_res.scalar_one_or_none():
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Inspection not found or consent revoked."})
        
    finding_res = await db.execute(select(MechanicFinding.id).where(MechanicFinding.inspection_id == inspection_id))
    has_finding = finding_res.first() is not None

    return ApiResponse.ok(_inspection_out(insp, mechanic_verified=has_finding))


@router.post("/inspections/{inspection_id}/findings")
async def add_finding(
    inspection_id: str,
    req: MechanicFindingCreate,
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    # Verify inspection and consent
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    insp = result.scalar_one_or_none()
    if not insp:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Inspection not found."})

    consent_res = await db.execute(
        select(ConsentRecord).where(
            ConsentRecord.mechanic_id == current_user.id,
            ConsentRecord.rider_id == insp.submitted_by,
            ConsentRecord.revoked_at == None
        )
    )
    if not consent_res.scalar_one_or_none():
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "No active consent from this rider."})

    finding = MechanicFinding(
        inspection_id=inspection_id,
        mechanic_id=current_user.id,
        tread_depth_mm=req.tread_depth_mm,
        pressure_psi=req.pressure_psi,
        puncture_count=req.puncture_count,
        mechanic_notes=req.mechanic_notes,
        recommended_action=req.recommended_action.value if req.recommended_action else None
    )
    db.add(finding)
    
    db.add(AuditEvent(
        actor_id=current_user.id,
        actor_role=current_user.role,
        event_type="mechanic.finding_recorded",
        resource_type="inspection",
        resource_id=inspection_id,
    ))
    
    await db.commit()
    await db.refresh(finding)

    return ApiResponse.ok({
        "id": finding.id,
        "inspection_id": finding.inspection_id,
        "created_at": finding.created_at.isoformat()
    })


@router.post("/service-records")
async def add_service_record(
    req: ServiceRecordCreate,
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    # Verify tyre position and consent
    result = await db.execute(
        select(TyrePosition, Vehicle)
        .join(Vehicle, Vehicle.id == TyrePosition.vehicle_id)
        .where(TyrePosition.id == req.tyre_position_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Tyre position not found."})
    tp, vehicle = row

    consent_res = await db.execute(
        select(ConsentRecord).where(
            ConsentRecord.mechanic_id == current_user.id,
            ConsentRecord.rider_id == vehicle.owner_id,
            ConsentRecord.revoked_at == None
        )
    )
    if not consent_res.scalar_one_or_none():
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "No active consent from this rider."})

    record = ServiceRecord(
        tyre_position_id=req.tyre_position_id,
        mechanic_id=current_user.id,
        service_type=req.service_type,
        odometer_km=req.odometer_km,
        cost_amount=req.cost_amount,
        notes=req.notes
    )
    db.add(record)
    
    db.add(AuditEvent(
        actor_id=current_user.id,
        actor_role=current_user.role,
        event_type="mechanic.service_recorded",
        resource_type="service_record",
        detail={"tyre_position_id": req.tyre_position_id, "service_type": req.service_type}
    ))
    
    await db.commit()
    await db.refresh(record)

    return ApiResponse.ok({
        "id": record.id,
        "created_at": record.created_at.isoformat()
    })
