"""GripWise Saathi — Business logic service for mechanic advocacy & engagement."""
from datetime import datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from backend.models import (
    User,
    MechanicProfile,
    LearningModule,
    MechanicModuleCompletion,
    MechanicBadge,
    MechanicEarnedBadge,
    CustomerReferral,
    MechanicFinding,
    ServiceRecord,
    AuditEvent,
    SaathiProgramInitiative,
)
from backend.services.saathi_seed import (
    SEED_MODULES,
    SEED_BADGES,
    SEED_INITIATIVES,
    SCORING_RULES,
)


async def ensure_seed_data(db: AsyncSession) -> None:
    """Idempotently seed learning modules, badges, and proposed initiatives if missing."""
    # 1. Modules
    result = await db.execute(select(func.count(LearningModule.id)))
    if (result.scalar() or 0) == 0:
        for mod_data in SEED_MODULES:
            db.add(LearningModule(**mod_data))
        await db.commit()

    # 2. Badges
    result = await db.execute(select(func.count(MechanicBadge.id)))
    if (result.scalar() or 0) == 0:
        for badge_data in SEED_BADGES:
            db.add(MechanicBadge(**badge_data))
        await db.commit()

    # 3. Initiatives
    result = await db.execute(select(func.count(SaathiProgramInitiative.id)))
    if (result.scalar() or 0) == 0:
        for init_data in SEED_INITIATIVES:
            db.add(SaathiProgramInitiative(**init_data))
        await db.commit()


def calculate_profile_completeness(user: User, profile: MechanicProfile | None) -> Tuple[int, Dict[str, bool]]:
    """Calculates profile completion percentage based on real stored fields."""
    checklist = {
        "display_name": bool(user.display_name),
        "workshop_name": bool(user.workshop_name),
        "workshop_city": bool(user.workshop_city),
        "years_experience": bool(profile and profile.years_experience is not None and profile.years_experience > 0),
        "specialization": bool(profile and profile.specialization),
        "workshop_address": bool(profile and profile.workshop_address),
        "contact_phone": bool((profile and profile.phone) or user.mobile),
        "bio": bool(profile and profile.bio),
    }
    completed_items = sum(1 for v in checklist.values() if v)
    percent = int((completed_items / len(checklist)) * 100)
    return percent, checklist


def determine_tier(points: int) -> Tuple[str, str | None, int]:
    """Determines transparent tier and points needed for next tier."""
    if points >= 500:
        return "Master Saathi", None, 0
    elif points >= 250:
        return "Gold Saathi", "Master Saathi", 500 - points
    elif points >= 100:
        return "Silver Saathi", "Gold Saathi", 250 - points
    else:
        return "Bronze Saathi", "Silver Saathi", 100 - points


async def sync_earned_badges(
    mechanic_id: str,
    user: User,
    profile: MechanicProfile | None,
    total_points: int,
    completed_modules_count: int,
    findings_count: int,
    services_count: int,
    completed_referrals_count: int,
    db: AsyncSession,
) -> List[str]:
    """Idempotently evaluates badge criteria and awards unearned badges."""
    # Fetch all badges and already earned badges
    badges_res = await db.execute(select(MechanicBadge))
    all_badges = {b.id: b for b in badges_res.scalars().all()}

    earned_res = await db.execute(
        select(MechanicEarnedBadge.badge_id).where(MechanicEarnedBadge.mechanic_id == mechanic_id)
    )
    already_earned = set(earned_res.scalars().all())

    profile_percent, _ = calculate_profile_completeness(user, profile)
    newly_earned: List[str] = []

    # Criteria checks
    # BADGE_WELCOME: profile >= 80%
    if "BADGE_WELCOME" in all_badges and "BADGE_WELCOME" not in already_earned and profile_percent >= 80:
        newly_earned.append("BADGE_WELCOME")

    # BADGE_LEARNING_PIONEER: at least 1 completed module
    if "BADGE_LEARNING_PIONEER" in all_badges and "BADGE_LEARNING_PIONEER" not in already_earned and completed_modules_count >= 1:
        newly_earned.append("BADGE_LEARNING_PIONEER")

    # BADGE_TYRE_SCHOLAR: all 5 modules completed
    if "BADGE_TYRE_SCHOLAR" in all_badges and "BADGE_TYRE_SCHOLAR" not in already_earned and completed_modules_count >= 5:
        newly_earned.append("BADGE_TYRE_SCHOLAR")

    # BADGE_INSPECTION_PRO: 3+ findings
    if "BADGE_INSPECTION_PRO" in all_badges and "BADGE_INSPECTION_PRO" not in already_earned and findings_count >= 3:
        newly_earned.append("BADGE_INSPECTION_PRO")

    # BADGE_SERVICE_CHAMPION: 3+ service records
    if "BADGE_SERVICE_CHAMPION" in all_badges and "BADGE_SERVICE_CHAMPION" not in already_earned and services_count >= 3:
        newly_earned.append("BADGE_SERVICE_CHAMPION")

    # BADGE_SAFETY_ADVOCATE: Module 5 completed + Silver tier (100+ points)
    if "BADGE_SAFETY_ADVOCATE" in all_badges and "BADGE_SAFETY_ADVOCATE" not in already_earned:
        ethics_comp = await db.execute(
            select(MechanicModuleCompletion).where(
                MechanicModuleCompletion.mechanic_id == mechanic_id,
                MechanicModuleCompletion.module_id == "mod-safety-ethics",
                MechanicModuleCompletion.passed == True,
            )
        )
        if ethics_comp.scalar_one_or_none() and total_points >= 100:
            newly_earned.append("BADGE_SAFETY_ADVOCATE")

    # Award newly earned badges
    for badge_id in newly_earned:
        db.add(MechanicEarnedBadge(mechanic_id=mechanic_id, badge_id=badge_id))
        db.add(
            AuditEvent(
                actor_id=mechanic_id,
                actor_role="MECHANIC",
                event_type="saathi.badge_earned",
                resource_type="badge",
                resource_id=badge_id,
                detail={"badge_id": badge_id, "earned_at": datetime.now().isoformat()},
            )
        )

    if newly_earned:
        await db.commit()

    return newly_earned


async def get_mechanic_stats(mechanic_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Calculates all real, verifiable activity counts, points, and tiers for a mechanic."""
    await ensure_seed_data(db)

    # User & profile
    user_res = await db.execute(select(User).where(User.id == mechanic_id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    profile_res = await db.execute(select(MechanicProfile).where(MechanicProfile.user_id == mechanic_id))
    profile = profile_res.scalar_one_or_none()

    # Activity 1: Module completions
    modules_comp_res = await db.execute(
        select(func.count(MechanicModuleCompletion.id)).where(
            MechanicModuleCompletion.mechanic_id == mechanic_id,
            MechanicModuleCompletion.passed == True,
        )
    )
    completed_modules_count = modules_comp_res.scalar() or 0

    # Total modules in catalogue
    total_mod_res = await db.execute(select(func.count(LearningModule.id)))
    total_modules_count = total_mod_res.scalar() or 0

    # Activity 2: Findings recorded
    findings_res = await db.execute(
        select(func.count(MechanicFinding.id)).where(MechanicFinding.mechanic_id == mechanic_id)
    )
    verified_findings_count = findings_res.scalar() or 0

    # Activity 3: Service records logged
    services_res = await db.execute(
        select(func.count(ServiceRecord.id)).where(ServiceRecord.mechanic_id == mechanic_id)
    )
    recorded_services_count = services_res.scalar() or 0

    # Activity 4: Customer referrals
    referrals_all_res = await db.execute(
        select(func.count(CustomerReferral.id)).where(CustomerReferral.mechanic_id == mechanic_id)
    )
    total_referrals_count = referrals_all_res.scalar() or 0

    referrals_comp_res = await db.execute(
        select(func.count(CustomerReferral.id)).where(
            CustomerReferral.mechanic_id == mechanic_id,
            CustomerReferral.status == "SERVICE_COMPLETED",
        )
    )
    completed_referrals_count = referrals_comp_res.scalar() or 0

    # Points calculation (Deterministic & Verifiable)
    # 50 pts per module + 25 pts per finding + 30 pts per service + 20 pts per completed follow-up
    total_points = (
        (completed_modules_count * 50)
        + (verified_findings_count * 25)
        + (recorded_services_count * 30)
        + (completed_referrals_count * 20)
    )

    tier, next_tier, points_to_next = determine_tier(total_points)

    # Sync and evaluate badges
    await sync_earned_badges(
        mechanic_id=mechanic_id,
        user=user,
        profile=profile,
        total_points=total_points,
        completed_modules_count=completed_modules_count,
        findings_count=verified_findings_count,
        services_count=recorded_services_count,
        completed_referrals_count=completed_referrals_count,
        db=db,
    )

    # Fetch badges
    all_badges_res = await db.execute(select(MechanicBadge))
    badges_list = all_badges_res.scalars().all()

    earned_badges_res = await db.execute(
        select(MechanicEarnedBadge).where(MechanicEarnedBadge.mechanic_id == mechanic_id)
    )
    earned_map = {eb.badge_id: eb.earned_at for eb in earned_badges_res.scalars().all()}

    all_badges_out = []
    earned_badges_out = []
    for b in badges_list:
        is_earned = b.id in earned_map
        badge_dict = {
            "id": b.id,
            "title": b.title,
            "description": b.description,
            "criteria_description": b.criteria_description,
            "icon_name": b.icon_name,
            "category": b.category,
            "points_threshold": b.points_threshold,
            "earned": is_earned,
            "earned_at": earned_map.get(b.id),
        }
        all_badges_out.append(badge_dict)
        if is_earned:
            earned_badges_out.append(badge_dict)

    profile_percent, checklist = calculate_profile_completeness(user, profile)

    return {
        "mechanic_id": user.id,
        "display_name": user.display_name,
        "workshop_name": user.workshop_name,
        "workshop_city": user.workshop_city,
        "profile_completeness_percent": profile_percent,
        "completion_checklist": checklist,
        "total_points": total_points,
        "tier": tier,
        "next_tier": next_tier,
        "points_to_next_tier": points_to_next,
        "completed_modules_count": completed_modules_count,
        "total_modules_count": total_modules_count,
        "verified_findings_count": verified_findings_count,
        "recorded_services_count": recorded_services_count,
        "total_referrals_count": total_referrals_count,
        "completed_referrals_count": completed_referrals_count,
        "badges_earned_count": len(earned_badges_out),
        "total_badges_count": len(all_badges_out),
        "earned_badges": earned_badges_out,
        "all_badges": all_badges_out,
        "scoring_rules": SCORING_RULES,
        "case_study_context": {
            "program_name": "GripWise Saathi — Mechanic Advocacy & Engagement",
            "challenge": "Eurogrip TORQ Challenge 4.0 (Case Study 4)",
            "purpose": "Empower two-wheeler mechanics through technical tyre skills, verified recognition, and customer trust rather than transactional discounts.",
            "disclaimer": "Proposed programme concept for Eurogrip TORQ Challenge 4.0 Case Study 4. Not an official corporate partnership or funded commercial program.",
        },
    }
