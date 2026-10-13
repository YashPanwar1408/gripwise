"""
GripWise Backend — SQLAlchemy ORM models.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import (
    String, Boolean, Integer, Float, Text, Date, DateTime,
    ForeignKey, Enum, ARRAY, UniqueConstraint, func, Index, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # RIDER | MECHANIC | ADMIN
    workshop_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    workshop_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    vehicles: Mapped[list["Vehicle"]] = relationship("Vehicle", back_populates="owner")
    audit_events: Mapped[list["AuditEvent"]] = relationship("AuditEvent", back_populates="actor")
    mechanic_profile: Mapped["MechanicProfile | None"] = relationship("MechanicProfile", back_populates="user", uselist=False)
    module_completions: Mapped[list["MechanicModuleCompletion"]] = relationship("MechanicModuleCompletion", back_populates="mechanic")
    earned_badges: Mapped[list["MechanicEarnedBadge"]] = relationship("MechanicEarnedBadge", back_populates="mechanic")
    referrals: Mapped[list["CustomerReferral"]] = relationship("CustomerReferral", back_populates="mechanic")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration: Mapped[str | None] = mapped_column(String(20), nullable=True)
    vehicle_type: Mapped[str] = mapped_column(String(20), default="MOTORCYCLE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner: Mapped["User"] = relationship("User", back_populates="vehicles")
    tyre_positions: Mapped[list["TyrePosition"]] = relationship("TyrePosition", back_populates="vehicle")


class TyrePosition(Base):
    __tablename__ = "tyre_positions"
    __table_args__ = (UniqueConstraint("vehicle_id", "position", name="uq_vehicle_position"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    vehicle_id: Mapped[str] = mapped_column(String(36), ForeignKey("vehicles.id"), nullable=False)
    position: Mapped[str] = mapped_column(String(20), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_spec: Mapped[str | None] = mapped_column(String(50), nullable=True)
    installed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    installed_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="tyre_positions")
    inspections: Mapped[list["Inspection"]] = relationship("Inspection", back_populates="tyre_position")


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tyre_position_id: Mapped[str] = mapped_column(String(36), ForeignKey("tyre_positions.id"), nullable=False)
    submitted_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    odometer_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    image_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    image_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    image_quality_status: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    quality_issues: Mapped[list | None] = mapped_column(JSON, nullable=True)
    inference_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recommended_action_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    inference_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tyre_position: Mapped["TyrePosition"] = relationship("TyrePosition", back_populates="inspections")
    submitter: Mapped["User"] = relationship("User", foreign_keys=[submitted_by])
    observations: Mapped[list["InspectionObservation"]] = relationship("InspectionObservation", back_populates="inspection", cascade="all, delete-orphan")


class InspectionObservation(Base):
    __tablename__ = "inspection_observations"
    __table_args__ = (UniqueConstraint("inspection_id", "field_name", name="uq_inspection_field"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    inspection_id: Mapped[str] = mapped_column(String(36), ForeignKey("inspections.id"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value_numeric: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    value_bool: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    confidence_tier: Mapped[str] = mapped_column(String(30), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    caveat: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="observations")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    actor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    actor_role: Mapped[str | None] = mapped_column(String(20), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    actor: Mapped["User | None"] = relationship("User", back_populates="audit_events")


class ConsentRecord(Base):
    __tablename__ = "consent_records"
    __table_args__ = (UniqueConstraint("rider_id", "mechanic_id", name="uq_rider_mechanic_consent"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    rider_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    mechanic_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    rider: Mapped["User"] = relationship("User", foreign_keys=[rider_id])
    mechanic: Mapped["User"] = relationship("User", foreign_keys=[mechanic_id])


class MechanicFinding(Base):
    __tablename__ = "mechanic_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    inspection_id: Mapped[str] = mapped_column(String(36), ForeignKey("inspections.id"), nullable=False)
    mechanic_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    tread_depth_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure_psi: Mapped[float | None] = mapped_column(Float, nullable=True)
    puncture_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mechanic_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    inspection: Mapped["Inspection"] = relationship("Inspection", backref="mechanic_findings")
    mechanic: Mapped["User"] = relationship("User", foreign_keys=[mechanic_id])


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tyre_position_id: Mapped[str] = mapped_column(String(36), ForeignKey("tyre_positions.id"), nullable=False)
    mechanic_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False) # TYRE_REPLACED, TYRE_ROTATED, PUNCTURE_REPAIRED, PRESSURE_ADJUSTED
    service_date: Mapped[date] = mapped_column(Date, default=date.today)
    odometer_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tyre_position: Mapped["TyrePosition"] = relationship("TyrePosition", backref="service_records")
    mechanic: Mapped["User"] = relationship("User", foreign_keys=[mechanic_id])


# ─────────────────────────── GripWise Saathi Engagement Models ───────────────────────────

class MechanicProfile(Base):
    __tablename__ = "mechanic_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(100), nullable=True)
    workshop_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    certifications: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="mechanic_profile")


class LearningModule(Base):
    __tablename__ = "learning_modules"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    module_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # INSPECTION, SAFETY, MAINTENANCE, COMMUNICATION, ETHICS
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    technical_source: Mapped[str] = mapped_column(String(255), nullable=False)
    quiz_questions: Mapped[list] = mapped_column(JSON, nullable=False)
    points_reward: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    completions: Mapped[list["MechanicModuleCompletion"]] = relationship("MechanicModuleCompletion", back_populates="module", cascade="all, delete-orphan")


class MechanicModuleCompletion(Base):
    __tablename__ = "mechanic_module_completions"
    __table_args__ = (UniqueConstraint("mechanic_id", "module_id", name="uq_mechanic_module_completion"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    mechanic_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    module_id: Mapped[str] = mapped_column(String(50), ForeignKey("learning_modules.id"), nullable=False)
    score_percent: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    mechanic: Mapped["User"] = relationship("User", back_populates="module_completions")
    module: Mapped["LearningModule"] = relationship("LearningModule", back_populates="completions")


class MechanicBadge(Base):
    __tablename__ = "mechanic_badges"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    criteria_description: Mapped[str] = mapped_column(Text, nullable=False)
    icon_name: Mapped[str] = mapped_column(String(50), nullable=False)
    points_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="ACHIEVEMENT", nullable=False)

    earned_by: Mapped[list["MechanicEarnedBadge"]] = relationship("MechanicEarnedBadge", back_populates="badge")


class MechanicEarnedBadge(Base):
    __tablename__ = "mechanic_earned_badges"
    __table_args__ = (UniqueConstraint("mechanic_id", "badge_id", name="uq_mechanic_badge"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    mechanic_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    badge_id: Mapped[str] = mapped_column(String(50), ForeignKey("mechanic_badges.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    mechanic: Mapped["User"] = relationship("User", back_populates="earned_badges")
    badge: Mapped["MechanicBadge"] = relationship("MechanicBadge", back_populates="earned_by")


class CustomerReferral(Base):
    __tablename__ = "customer_referrals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    mechanic_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    customer_name_masked: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone_masked: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vehicle_model: Mapped[str] = mapped_column(String(100), nullable=False)
    tyre_need: Mapped[str] = mapped_column(String(50), nullable=False)  # REPLACEMENT_INSPECTION, PRESSURE_CHECK, PUNCTURE_FOLLOWUP, TREAD_WEAR_MONITORING
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, CONTACTED, SERVICE_COMPLETED, EXPIRED
    consent_confirmed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    service_record_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("service_records.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    mechanic: Mapped["User"] = relationship("User", back_populates="referrals")
    service_record: Mapped["ServiceRecord | None"] = relationship("ServiceRecord")


class SaathiProgramInitiative(Base):
    __tablename__ = "saathi_program_initiatives"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # TOOL_SUPPORT, BRAND_WORKSHOP, SAFETY_SIGNAGE
    description: Mapped[str] = mapped_column(Text, nullable=False)
    eligibility_level: Mapped[str] = mapped_column(String(50), nullable=False)  # BRONZE, SILVER, GOLD, MASTER
    status: Mapped[str] = mapped_column(String(50), default="PROPOSED_CONCEPT", nullable=False)
    tool_specs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
