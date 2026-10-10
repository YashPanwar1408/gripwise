"""GripWise Backend — Vehicles and tyre-positions router."""
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import User, Vehicle, TyrePosition
from backend.schemas import ApiResponse, VehicleCreate, VehicleOut, TyrePositionCreate, TyrePositionOut
from backend.auth import get_current_user

log = structlog.get_logger()
router = APIRouter()


def _vehicle_out(v: Vehicle) -> dict:
    return {
        "vehicle_id": v.id,
        "make": v.make,
        "model": v.model,
        "year": v.year,
        "registration": v.registration,
        "vehicle_type": v.vehicle_type,
        "tyre_positions": [
            {
                "tyre_position_id": tp.id,
                "vehicle_id": tp.vehicle_id,
                "position": tp.position,
                "brand": tp.brand,
                "model_name": tp.model_name,
                "size_spec": tp.size_spec,
                "installed_at": tp.installed_at.isoformat() if tp.installed_at else None,
                "installed_km": tp.installed_km,
                "created_at": tp.created_at.isoformat(),
            }
            for tp in v.tyre_positions
        ],
        "created_at": v.created_at.isoformat(),
    }


@router.post("", status_code=201)
async def create_vehicle(
    body: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    vehicle = Vehicle(
        owner_id=current_user.id,
        make=body.make,
        model=body.model,
        year=body.year,
        registration=body.registration,
        vehicle_type=body.vehicle_type.value,
    )
    db.add(vehicle)
    await db.flush()
    await db.refresh(vehicle)
    log.info("vehicle.created", vehicle_id=vehicle.id, user_id=current_user.id)
    return ApiResponse.ok({
        "vehicle_id": vehicle.id,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "registration": vehicle.registration,
        "vehicle_type": vehicle.vehicle_type,
        "tyre_positions": [],
        "created_at": vehicle.created_at.isoformat(),
    })


@router.get("")
async def list_vehicles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vehicle)
        .where(Vehicle.owner_id == current_user.id, Vehicle.deleted_at == None)
        .options(selectinload(Vehicle.tyre_positions))
        .order_by(Vehicle.created_at.desc())
    )
    vehicles = result.scalars().all()
    return ApiResponse.ok({"vehicles": [_vehicle_out(v) for v in vehicles]})


@router.get("/{vehicle_id}")
async def get_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vehicle)
        .where(Vehicle.id == vehicle_id, Vehicle.owner_id == current_user.id, Vehicle.deleted_at == None)
        .options(selectinload(Vehicle.tyre_positions))
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Vehicle not found"})
    return ApiResponse.ok(_vehicle_out(vehicle))


@router.post("/{vehicle_id}/tyre-positions", status_code=201)
async def add_tyre_position(
    vehicle_id: str,
    body: TyrePositionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.owner_id == current_user.id, Vehicle.deleted_at == None)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Vehicle not found"})

    # Check for duplicate position
    existing = await db.execute(
        select(TyrePosition).where(TyrePosition.vehicle_id == vehicle_id, TyrePosition.position == body.position.value)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(422, detail={"code": "VALIDATION_ERROR", "message": f"Position {body.position.value} already registered for this vehicle"})

    tp = TyrePosition(
        vehicle_id=vehicle_id,
        position=body.position.value,
        brand=body.brand,
        model_name=body.model_name,
        size_spec=body.size_spec,
        installed_at=body.installed_at,
        installed_km=body.installed_km,
    )
    db.add(tp)
    await db.flush()
    await db.refresh(tp)
    log.info("tyre_position.created", tp_id=tp.id, vehicle_id=vehicle_id)
    return ApiResponse.ok({
        "tyre_position_id": tp.id,
        "vehicle_id": tp.vehicle_id,
        "position": tp.position,
        "brand": tp.brand,
        "model_name": tp.model_name,
        "size_spec": tp.size_spec,
        "installed_at": tp.installed_at.isoformat() if tp.installed_at else None,
        "installed_km": tp.installed_km,
        "created_at": tp.created_at.isoformat(),
    })
