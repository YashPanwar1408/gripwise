"""GripWise Backend — Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Any, Optional, List
from datetime import datetime, date
from enum import Enum


# ─────────────────────────── Envelope ───────────────────────────

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None

    @classmethod
    def ok(cls, data: Any) -> "ApiResponse":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, code: str, message: str, details: Optional[dict] = None) -> "ApiResponse":
        return cls(success=False, error=ErrorDetail(code=code, message=message, details=details))


# ─────────────────────────── Enums ───────────────────────────

class UserRole(str, Enum):
    RIDER = "RIDER"
    MECHANIC = "MECHANIC"
    ADMIN = "ADMIN"


class VehicleType(str, Enum):
    MOTORCYCLE = "MOTORCYCLE"
    SCOOTER = "SCOOTER"
    BICYCLE = "BICYCLE"
    OTHER = "OTHER"


class TyrePositionEnum(str, Enum):
    FRONT = "FRONT"
    REAR = "REAR"
    FRONT_LEFT = "FRONT_LEFT"
    FRONT_RIGHT = "FRONT_RIGHT"
    REAR_LEFT = "REAR_LEFT"
    REAR_RIGHT = "REAR_RIGHT"


class ConfidenceTier(str, Enum):
    HIGH = "HIGH_CONFIDENCE"
    MEDIUM = "MEDIUM_CONFIDENCE"
    LOW = "LOW_CONFIDENCE"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class InspectionStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class RecommendedAction(str, Enum):
    OK = "ok"
    MONITOR = "monitor"
    INSPECT_SOON = "inspect_soon"
    REPLACE_URGENTLY = "replace_urgently"
    SEEK_MECHANIC_NOW = "seek_mechanic_now"
    ANALYSIS_FAILED = "analysis_failed"


# ─────────────────────────── Auth ───────────────────────────

class RegisterRequest(BaseModel):
    display_name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    role: UserRole = UserRole.RIDER
    password: str
    workshop_name: Optional[str] = None
    workshop_city: Optional[str] = None

    @model_validator(mode="after")
    def check_contact(self) -> "RegisterRequest":
        if not self.email and not self.mobile:
            raise ValueError("Either email or mobile is required")
        if self.role == UserRole.MECHANIC and not self.workshop_name:
            raise ValueError("workshop_name is required for MECHANIC role")
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return self


class LoginRequest(BaseModel):
    credential: str    # email or mobile
    password: str


class TokenResponse(BaseModel):
    user_id: str
    role: str
    display_name: str
    access_token: str
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ─────────────────────────── Vehicles ───────────────────────────

class VehicleCreate(BaseModel):
    make: str
    model: str
    year: Optional[int] = None
    registration: Optional[str] = None
    vehicle_type: VehicleType = VehicleType.MOTORCYCLE


class TyrePositionCreate(BaseModel):
    position: TyrePositionEnum
    brand: Optional[str] = None
    model_name: Optional[str] = None
    size_spec: Optional[str] = None
    installed_at: Optional[date] = None
    installed_km: Optional[int] = None

    model_config = {"protected_namespaces": ()}


class TyrePositionOut(BaseModel):
    tyre_position_id: str
    vehicle_id: str
    position: str
    brand: Optional[str]
    model_name: Optional[str]
    size_spec: Optional[str]
    installed_at: Optional[date]
    installed_km: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class VehicleOut(BaseModel):
    vehicle_id: str
    make: str
    model: str
    year: Optional[int]
    registration: Optional[str]
    vehicle_type: str
    tyre_positions: List[TyrePositionOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────── Inspections ───────────────────────────

class InspectionObservationOut(BaseModel):
    field: str
    value: Optional[Any]
    confidence: str
    explanation: str
    caveat: Optional[str]

    model_config = {"from_attributes": True}


class InspectionOut(BaseModel):
    inspection_id: str
    tyre_position_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    inference_provider: Optional[str]
    model_version: Optional[str]
    image_quality: dict
    recommended_action: Optional[str]
    recommended_action_explanation: Optional[str]
    observations: List[InspectionObservationOut] = []
    inference_ms: Optional[float]
    mechanic_verified: bool = False

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class InspectionSummary(BaseModel):
    inspection_id: str
    tyre_position_id: str
    status: str
    recommended_action: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────── Mechanic Module ───────────────────────────

class ConsentRecordCreate(BaseModel):
    mechanic_id: str

class ConsentRecordOut(BaseModel):
    id: str
    rider_id: str
    mechanic_id: str
    granted_at: datetime
    revoked_at: Optional[datetime]
    mechanic_name: Optional[str] = None
    workshop_name: Optional[str] = None

    model_config = {"from_attributes": True}


class MechanicFindingCreate(BaseModel):
    tread_depth_mm: Optional[float] = None
    pressure_psi: Optional[float] = None
    puncture_count: Optional[int] = None
    mechanic_notes: Optional[str] = None
    recommended_action: Optional[RecommendedAction] = None

class MechanicFindingOut(BaseModel):
    id: str
    mechanic_id: str
    mechanic_name: Optional[str] = None
    tread_depth_mm: Optional[float]
    pressure_psi: Optional[float]
    puncture_count: Optional[int]
    mechanic_notes: Optional[str]
    recommended_action: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ServiceRecordCreate(BaseModel):
    tyre_position_id: str
    service_type: str # TYRE_REPLACED, TYRE_ROTATED, PUNCTURE_REPAIRED, PRESSURE_ADJUSTED
    odometer_km: Optional[int] = None
    cost_amount: Optional[float] = None
    notes: Optional[str] = None

class ServiceRecordOut(BaseModel):
    id: str
    tyre_position_id: str
    mechanic_id: str
    mechanic_name: Optional[str] = None
    service_type: str
    service_date: date
    odometer_km: Optional[int]
    cost_amount: Optional[float]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────── GripWise Saathi Schemas ───────────────────────────

class MechanicProfileUpdate(BaseModel):
    years_experience: Optional[int] = None
    specialization: Optional[str] = None
    workshop_address: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    certifications: Optional[List[str]] = None


class MechanicProfileOut(BaseModel):
    user_id: str
    display_name: str
    workshop_name: Optional[str]
    workshop_city: Optional[str]
    years_experience: Optional[int] = None
    specialization: Optional[str] = None
    workshop_address: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    certifications: Optional[List[str]] = None
    completion_percent: int
    completion_checklist: dict

    model_config = {"from_attributes": True}


class QuizQuestion(BaseModel):
    id: int
    prompt: str
    options: List[str]
    correct_index: int
    explanation: str


class LearningModuleSummaryOut(BaseModel):
    id: str
    module_code: str
    title: str
    category: str
    estimated_minutes: int
    summary: str
    points_reward: int
    technical_source: str
    completed: bool = False
    score_percent: Optional[float] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LearningModuleDetailOut(LearningModuleSummaryOut):
    content_markdown: str
    quiz_questions: List[QuizQuestion]


class QuizSubmissionRequest(BaseModel):
    answers: List[int]


class QuizQuestionFeedback(BaseModel):
    question_id: int
    selected_index: int
    correct_index: int
    is_correct: bool
    explanation: str


class QuizResultOut(BaseModel):
    module_id: str
    score_percent: float
    passed: bool
    points_awarded: int
    total_points: int
    tier: str
    newly_earned_badges: List[str]
    feedback: List[QuizQuestionFeedback]


class MechanicBadgeOut(BaseModel):
    id: str
    title: str
    description: str
    criteria_description: str
    icon_name: str
    category: str
    points_threshold: Optional[int] = None
    earned: bool = False
    earned_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CustomerReferralCreate(BaseModel):
    customer_name_masked: str
    customer_phone_masked: Optional[str] = None
    vehicle_model: str
    tyre_need: str  # REPLACEMENT_INSPECTION, PRESSURE_CHECK, PUNCTURE_FOLLOWUP, TREAD_WEAR_MONITORING
    notes: Optional[str] = None
    consent_confirmed: bool = False

    @field_validator("customer_name_masked")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Customer reference name is required")
        return clean


class CustomerReferralUpdate(BaseModel):
    status: str  # PENDING, CONTACTED, SERVICE_COMPLETED, EXPIRED
    notes: Optional[str] = None
    service_record_id: Optional[str] = None


class CustomerReferralOut(BaseModel):
    id: str
    mechanic_id: str
    customer_name_masked: str
    customer_phone_masked: Optional[str] = None
    vehicle_model: str
    tyre_need: str
    status: str
    consent_confirmed: bool
    service_record_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScoringRuleOut(BaseModel):
    activity: str
    points: int
    description: str
    ethical_safeguard: str


class SaathiDashboardStatsOut(BaseModel):
    mechanic_id: str
    display_name: str
    workshop_name: Optional[str]
    workshop_city: Optional[str]
    profile_completeness_percent: int
    total_points: int
    tier: str
    next_tier: Optional[str] = None
    points_to_next_tier: int = 0
    completed_modules_count: int
    total_modules_count: int
    verified_findings_count: int
    recorded_services_count: int
    total_referrals_count: int
    completed_referrals_count: int
    badges_earned_count: int
    total_badges_count: int
    earned_badges: List[MechanicBadgeOut]
    all_badges: List[MechanicBadgeOut]
    scoring_rules: List[ScoringRuleOut]
    case_study_context: dict


class SaathiProgramInitiativeOut(BaseModel):
    id: str
    title: str
    category: str
    description: str
    eligibility_level: str
    status: str
    tool_specs: Optional[dict] = None

    model_config = {"from_attributes": True}
