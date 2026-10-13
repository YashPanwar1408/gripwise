"""GripWise backend API for mechanic profile, learning, and follow-up features.

Provides:
- Mechanic Professional Profile with verifiable completion
- Tyre-Care Learning Hub (educational modules, quizzes, transparent guidance)
- Verifiable Recognition, Points & Badges (anti-brand-bias, transparent scoring)
- Consent-aware Customer Referrals & Follow-ups
- Optional partner programme concepts, disabled by default
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import structlog

from backend.database import get_db
from backend.config import settings
from backend.models import (
    User,
    MechanicProfile,
    LearningModule,
    MechanicModuleCompletion,
    MechanicBadge,
    MechanicEarnedBadge,
    CustomerReferral,
    AuditEvent,
    SaathiProgramInitiative,
)
from backend.schemas import (
    ApiResponse,
    MechanicProfileUpdate,
    MechanicProfileOut,
    LearningModuleSummaryOut,
    LearningModuleDetailOut,
    QuizSubmissionRequest,
    QuizResultOut,
    QuizQuestionFeedback,
    MechanicBadgeOut,
    CustomerReferralCreate,
    CustomerReferralUpdate,
    CustomerReferralOut,
    SaathiDashboardStatsOut,
    SaathiProgramInitiativeOut,
)
from backend.auth import get_current_user
from backend.services.saathi_service import (
    ensure_seed_data,
    get_mechanic_stats,
    calculate_profile_completeness,
    determine_tier,
    sync_earned_badges,
)

log = structlog.get_logger()
router = APIRouter()


async def require_mechanic(user: User = Depends(get_current_user)) -> User:
    """Enforces server-side role authorization: MECHANIC role required."""
    if user.role != "MECHANIC":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Mechanic role required for Mechanic Growth features."},
        )
    return user


# ── Dashboard & Recognition ────────────────────────────────────────

@router.get("/dashboard", response_model=ApiResponse)
async def get_saathi_dashboard(
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Returns comprehensive real engagement metrics, tier, points, and badge achievements."""
    stats = await get_mechanic_stats(current_user.id, db)
    return ApiResponse.ok(stats)


# ── Professional Profile ───────────────────────────────────────────

@router.get("/profile", response_model=ApiResponse)
async def get_mechanic_profile(
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves the mechanic's professional profile and completion checklist."""
    profile_res = await db.execute(
        select(MechanicProfile).where(MechanicProfile.user_id == current_user.id)
    )
    profile = profile_res.scalar_one_or_none()

    percent, checklist = calculate_profile_completeness(current_user, profile)

    out = {
        "user_id": current_user.id,
        "display_name": current_user.display_name,
        "workshop_name": current_user.workshop_name,
        "workshop_city": current_user.workshop_city,
        "years_experience": profile.years_experience if profile else None,
        "specialization": profile.specialization if profile else None,
        "workshop_address": profile.workshop_address if profile else None,
        "phone": (profile.phone if profile and profile.phone else current_user.mobile),
        "bio": profile.bio if profile else None,
        "certifications": profile.certifications if profile else None,
        "completion_percent": percent,
        "completion_checklist": checklist,
    }
    return ApiResponse.ok(out)


@router.put("/profile", response_model=ApiResponse)
async def update_mechanic_profile(
    req: MechanicProfileUpdate,
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Updates mechanic professional profile and recalculates profile completion."""
    profile_res = await db.execute(
        select(MechanicProfile).where(MechanicProfile.user_id == current_user.id)
    )
    profile = profile_res.scalar_one_or_none()

    if not profile:
        profile = MechanicProfile(user_id=current_user.id)
        db.add(profile)

    if req.years_experience is not None:
        profile.years_experience = req.years_experience
    if req.specialization is not None:
        profile.specialization = req.specialization.strip()
    if req.workshop_address is not None:
        profile.workshop_address = req.workshop_address.strip()
    if req.phone is not None:
        profile.phone = req.phone.strip()
    if req.bio is not None:
        profile.bio = req.bio.strip()
    if req.certifications is not None:
        profile.certifications = req.certifications

    db.add(
        AuditEvent(
            actor_id=current_user.id,
            actor_role="MECHANIC",
            event_type="saathi.profile_updated",
            resource_type="mechanic_profile",
            resource_id=current_user.id,
        )
    )

    await db.commit()
    await db.refresh(profile)

    # Trigger potential badge award if profile now >= 80%
    await get_mechanic_stats(current_user.id, db)

    percent, checklist = calculate_profile_completeness(current_user, profile)

    out = {
        "user_id": current_user.id,
        "display_name": current_user.display_name,
        "workshop_name": current_user.workshop_name,
        "workshop_city": current_user.workshop_city,
        "years_experience": profile.years_experience,
        "specialization": profile.specialization,
        "workshop_address": profile.workshop_address,
        "phone": profile.phone or current_user.mobile,
        "bio": profile.bio,
        "certifications": profile.certifications,
        "completion_percent": percent,
        "completion_checklist": checklist,
    }
    return ApiResponse.ok(out)


# ── Tyre-Care Learning Hub ─────────────────────────────────────────

@router.get("/learning/modules", response_model=ApiResponse)
async def list_learning_modules(
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Lists all educational modules with the current mechanic's completion status."""
    await ensure_seed_data(db)

    modules_res = await db.execute(select(LearningModule).order_by(LearningModule.module_code.asc()))
    modules = modules_res.scalars().all()

    completions_res = await db.execute(
        select(MechanicModuleCompletion).where(
            MechanicModuleCompletion.mechanic_id == current_user.id
        )
    )
    comp_map = {c.module_id: c for c in completions_res.scalars().all()}

    out = []
    for m in modules:
        c = comp_map.get(m.id)
        out.append({
            "id": m.id,
            "module_code": m.module_code,
            "title": m.title,
            "category": m.category,
            "estimated_minutes": m.estimated_minutes,
            "summary": m.summary,
            "points_reward": m.points_reward,
            "technical_source": m.technical_source,
            "completed": bool(c and c.passed),
            "score_percent": c.score_percent if c else None,
            "completed_at": c.completed_at.isoformat() if c else None,
        })

    return ApiResponse.ok({"modules": out})


@router.get("/learning/modules/{module_id}", response_model=ApiResponse)
async def get_learning_module_detail(
    module_id: str,
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Fetches full learning module content and quiz questions."""
    await ensure_seed_data(db)

    result = await db.execute(select(LearningModule).where(LearningModule.id == module_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Educational module not found."},
        )

    comp_res = await db.execute(
        select(MechanicModuleCompletion).where(
            MechanicModuleCompletion.mechanic_id == current_user.id,
            MechanicModuleCompletion.module_id == module_id,
        )
    )
    c = comp_res.scalar_one_or_none()

    questions = m.quiz_questions or []

    out = {
        "id": m.id,
        "module_code": m.module_code,
        "title": m.title,
        "category": m.category,
        "estimated_minutes": m.estimated_minutes,
        "summary": m.summary,
        "content_markdown": m.content_markdown,
        "points_reward": m.points_reward,
        "technical_source": m.technical_source,
        "completed": bool(c and c.passed),
        "score_percent": c.score_percent if c else None,
        "completed_at": c.completed_at.isoformat() if c else None,
        "quiz_questions": questions,
    }
    return ApiResponse.ok(out)


@router.post("/learning/modules/{module_id}/quiz", response_model=ApiResponse)
async def submit_learning_quiz(
    module_id: str,
    req: QuizSubmissionRequest,
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Submits answers for a module quiz, calculates score, and awards idempotent points."""
    await ensure_seed_data(db)

    result = await db.execute(select(LearningModule).where(LearningModule.id == module_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Educational module not found."},
        )

    questions = m.quiz_questions or []
    if len(req.answers) != len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ANSWERS",
                "message": f"Expected {len(questions)} answers, received {len(req.answers)}.",
            },
        )

    correct_count = 0
    feedback: List[dict] = []
    for i, q in enumerate(questions):
        selected = req.answers[i]
        correct = q["correct_index"]
        is_corr = (selected == correct)
        if is_corr:
            correct_count += 1
        feedback.append({
            "question_id": q.get("id", i + 1),
            "selected_index": selected,
            "correct_index": correct,
            "is_correct": is_corr,
            "explanation": q.get("explanation", ""),
        })

    score_percent = round((correct_count / len(questions)) * 100, 1)
    passed = score_percent >= 66.0  # At least 2 out of 3 questions correct

    # Check prior completion
    comp_res = await db.execute(
        select(MechanicModuleCompletion).where(
            MechanicModuleCompletion.mechanic_id == current_user.id,
            MechanicModuleCompletion.module_id == module_id,
        )
    )
    existing_comp = comp_res.scalar_one_or_none()

    points_awarded = 0
    if passed:
        if not existing_comp:
            # First time passing: award points!
            new_comp = MechanicModuleCompletion(
                mechanic_id=current_user.id,
                module_id=module_id,
                score_percent=score_percent,
                passed=True,
            )
            db.add(new_comp)
            points_awarded = m.points_reward
            db.add(
                AuditEvent(
                    actor_id=current_user.id,
                    actor_role="MECHANIC",
                    event_type="saathi.module_passed",
                    resource_type="learning_module",
                    resource_id=module_id,
                    detail={"score": score_percent, "points_awarded": points_awarded},
                )
            )
            await db.commit()
        else:
            # Retake: update score if higher, but NEVER duplicate points (idempotent safeguard)
            if score_percent > existing_comp.score_percent:
                existing_comp.score_percent = score_percent
                existing_comp.passed = True
                await db.commit()

    # Re-calculate stats and newly earned badges
    stats = await get_mechanic_stats(current_user.id, db)

    out = {
        "module_id": module_id,
        "score_percent": score_percent,
        "passed": passed,
        "points_awarded": points_awarded,
        "total_points": stats["total_points"],
        "tier": stats["tier"],
        "newly_earned_badges": [b["id"] for b in stats["earned_badges"]],
        "feedback": feedback,
    }
    return ApiResponse.ok(out)


# ── Transparent Recognition & Badges ───────────────────────────────

@router.get("/badges", response_model=ApiResponse)
async def list_badges(
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Lists all participation badges and indicates which ones are earned by the mechanic."""
    stats = await get_mechanic_stats(current_user.id, db)
    return ApiResponse.ok({"badges": stats["all_badges"]})


# ── Customer Engagement & Referrals ────────────────────────────────

@router.get("/referrals", response_model=ApiResponse)
async def list_customer_referrals(
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Lists customer follow-ups and referrals created by this mechanic only."""
    result = await db.execute(
        select(CustomerReferral)
        .where(CustomerReferral.mechanic_id == current_user.id)
        .order_by(CustomerReferral.created_at.desc())
    )
    referrals = result.scalars().all()

    out = []
    for r in referrals:
        out.append({
            "id": r.id,
            "mechanic_id": r.mechanic_id,
            "customer_name_masked": r.customer_name_masked,
            "customer_phone_masked": r.customer_phone_masked,
            "vehicle_model": r.vehicle_model,
            "tyre_need": r.tyre_need,
            "status": r.status,
            "consent_confirmed": r.consent_confirmed,
            "service_record_id": r.service_record_id,
            "notes": r.notes,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat(),
        })

    return ApiResponse.ok({"referrals": out})


@router.post("/referrals", response_model=ApiResponse)
async def create_customer_referral(
    req: CustomerReferralCreate,
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Logs a new customer tyre safety follow-up or referral (consent-aware, privacy protected)."""
    if not req.consent_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CUSTOMER_CONSENT_REQUIRED",
                "message": "Customer agreement is required before saving a follow-up.",
            },
        )

    referral = CustomerReferral(
        mechanic_id=current_user.id,
        customer_name_masked=req.customer_name_masked,
        customer_phone_masked=req.customer_phone_masked,
        vehicle_model=req.vehicle_model.strip(),
        tyre_need=req.tyre_need.strip(),
        consent_confirmed=req.consent_confirmed,
        notes=req.notes,
        status="PENDING",
    )
    db.add(referral)

    db.add(
        AuditEvent(
            actor_id=current_user.id,
            actor_role="MECHANIC",
            event_type="saathi.referral_created",
            resource_type="customer_referral",
            resource_id=referral.id,
            detail={"tyre_need": req.tyre_need, "vehicle_model": req.vehicle_model},
        )
    )

    await db.commit()
    await db.refresh(referral)

    out = {
        "id": referral.id,
        "mechanic_id": referral.mechanic_id,
        "customer_name_masked": referral.customer_name_masked,
        "customer_phone_masked": referral.customer_phone_masked,
        "vehicle_model": referral.vehicle_model,
        "tyre_need": referral.tyre_need,
        "status": referral.status,
        "consent_confirmed": referral.consent_confirmed,
        "service_record_id": referral.service_record_id,
        "notes": referral.notes,
        "created_at": referral.created_at.isoformat(),
        "updated_at": referral.updated_at.isoformat(),
    }
    return ApiResponse.ok(out)


@router.patch("/referrals/{referral_id}", response_model=ApiResponse)
async def update_customer_referral_status(
    referral_id: str,
    req: CustomerReferralUpdate,
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Updates follow-up referral status (e.g. marked CONTACTED, SERVICE_COMPLETED)."""
    result = await db.execute(
        select(CustomerReferral).where(
            CustomerReferral.id == referral_id,
            CustomerReferral.mechanic_id == current_user.id,
        )
    )
    referral = result.scalar_one_or_none()
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Customer referral record not found or unauthorized."},
        )

    allowed_statuses = {"PENDING", "CONTACTED", "SERVICE_COMPLETED", "EXPIRED"}
    if req.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATUS", "message": f"Status must be one of: {allowed_statuses}"},
        )

    referral.status = req.status
    if req.notes is not None:
        referral.notes = req.notes
    if req.service_record_id is not None:
        referral.service_record_id = req.service_record_id

    db.add(
        AuditEvent(
            actor_id=current_user.id,
            actor_role="MECHANIC",
            event_type="saathi.referral_updated",
            resource_type="customer_referral",
            resource_id=referral.id,
            detail={"new_status": req.status},
        )
    )

    await db.commit()
    await db.refresh(referral)

    out = {
        "id": referral.id,
        "mechanic_id": referral.mechanic_id,
        "customer_name_masked": referral.customer_name_masked,
        "customer_phone_masked": referral.customer_phone_masked,
        "vehicle_model": referral.vehicle_model,
        "tyre_need": referral.tyre_need,
        "status": referral.status,
        "consent_confirmed": referral.consent_confirmed,
        "service_record_id": referral.service_record_id,
        "notes": referral.notes,
        "created_at": referral.created_at.isoformat(),
        "updated_at": referral.updated_at.isoformat(),
    }
    return ApiResponse.ok(out)


# ── Optional partner programme concepts ──

@router.get("/initiatives", response_model=ApiResponse)
async def list_program_initiatives(
    current_user: User = Depends(require_mechanic),
    db: AsyncSession = Depends(get_db),
):
    """Returns optional partner programme concepts when enabled in application configuration."""
    if not settings.ENABLE_PARTNER_PROGRAMMES:
        return ApiResponse.ok({
            "case_study": "Optional partner programme concepts",
            "program_disclaimer": "Disabled by configuration. No partner offers are active.",
            "initiatives": [],
        })

    await ensure_seed_data(db)

    result = await db.execute(select(SaathiProgramInitiative).order_by(SaathiProgramInitiative.title.asc()))
    initiatives = result.scalars().all()

    out = []
    for init in initiatives:
        out.append({
            "id": init.id,
            "title": init.title,
            "category": init.category,
            "description": init.description,
            "eligibility_level": init.eligibility_level,
            "status": init.status,
            "tool_specs": {
                key: value
                for key, value in (init.tool_specs or {}).items()
                if key != "case_study_source"
            },
        })

    return ApiResponse.ok({
        "case_study": "Optional partner programme concepts",
        "program_disclaimer": "Concept examples only. No manufacturer partnership, sponsorship, funding, or accreditation is confirmed.",
        "initiatives": out,
    })
