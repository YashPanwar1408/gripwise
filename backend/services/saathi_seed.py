"""Seed content for Mechanic Growth learning and optional partner concepts.

Includes:
- Standard curriculum modules with verified engineering guidance (ISO/ETRTO standards)
- Standard badges catalogue
- Proposal-only partner programme examples, shown only when enabled
"""
from typing import List, Dict, Any

SEED_MODULES: List[Dict[str, Any]] = [
    {
        "id": "mod-tread-wear",
        "module_code": "MOD-01",
        "title": "Tread Wear Patterns, TWI & Safety Limits",
        "category": "INSPECTION",
        "estimated_minutes": 10,
        "summary": "Master physical tread depth inspection, Tread Wear Indicator (TWI) identification, and diagnosing irregular wear patterns.",
        "content_markdown": """# Tread Wear Patterns, TWI & Safety Limits

### Technical Background & Industry Reference
Tread grooves on two-wheeler tyres are engineered to evacuate water and ensure grip during cornering, braking, and straight-line travel. As the tread wears down, the tyre loses its water channeling capacity, drastically increasing stopping distance and the risk of hydroplaning/skidding.

### Key Inspection Checkpoints
1. **Tread Wear Indicators (TWI):**
   - Look for triangular marks or letters 'TWI' embossed on the upper tyre shoulder.
   - Follow the indicator inward to find small raised rubber bars (typically 0.8 mm to 1.0 mm for two-wheelers in India / ISO standards) inside the tread grooves.
   - When the adjacent tread surface is flush with the TWI bar, the tyre has reached its legal and functional end-of-life and must be replaced immediately.

2. **Diagnosing Wear Patterns:**
   - **Center Tread Accelerated Wear:** Typically caused by persistent over-inflation or extended straight-line highway cruising on hard compounds.
   - **Shoulder / Edge Accelerated Wear:** Typically caused by persistent under-inflation or low tyre pressure while carrying pillion loads.
   - **Cupping / Scalloping Wear:** Caused by worn front fork bushings, misaligned wheels, or degraded shock absorbers causing the tyre to bounce microscopically.
   - **One-Sided Shoulder Wear:** Indicates wheel or axle misalignment or bent suspension components.

### Mechanic Recommendation Standard
- Minimum safe depth for monsoon riding: **2.0 mm** (recommended proactive replacement).
- Absolute safety threshold: **1.0 mm** (legal minimum in many jurisdictions is 0.8mm-1.0mm).
- Never scrape or re-groove motorcycle tyres under any circumstances.

> **Notice:** General tyre engineering guidance based on ISO 4223 & ETRTO standards. This is educational guidance and not an official manufacturer endorsement.
""",
        "technical_source": "ISO 4223 & ETRTO Standards on Two-Wheeler Pneumatic Tyres",
        "points_reward": 50,
        "quiz_questions": [
            {
                "id": 1,
                "prompt": "What does it mean when the tyre tread surface becomes completely level with the TWI (Tread Wear Indicator) bar?",
                "options": [
                    "The tyre is broken in and ready for high-speed cruising",
                    "The tyre has reached its minimum legal/safety limit and must be replaced immediately",
                    "The tyre needs to be rotated to the opposite wheel position",
                    "The tyre pressure must be reduced by 5 PSI"
                ],
                "correct_index": 1,
                "explanation": "When tread depth wears down to the level of the TWI bar, the remaining groove depth is insufficient to channel water safely, indicating urgent replacement is required."
            },
            {
                "id": 2,
                "prompt": "Which operating condition is the primary cause of accelerated wear along both outer shoulders of a motorcycle tyre?",
                "options": [
                    "Persistent under-inflation (running at too low PSI)",
                    "Excessive tyre pressure (over-inflation)",
                    "Driving on newly paved asphalt roads",
                    "Using nitrogen instead of atmospheric air"
                ],
                "correct_index": 0,
                "explanation": "Under-inflation allows the center of the tyre crown to flex upward and sink inward, putting excessive load and friction on the outer tread shoulders."
            },
            {
                "id": 3,
                "prompt": "Why is tread re-grooving or carving artificial grooves strictly prohibited on two-wheeler tyres?",
                "options": [
                    "It makes the tyre look asymmetrical to riders",
                    "It cuts directly into the critical casing plies and breaker belt, creating imminent blowout danger",
                    "It increases fuel consumption by 50%",
                    "It voids only the cosmetic warranty"
                ],
                "correct_index": 1,
                "explanation": "Motorcycle tyres have thin undertread rubber; re-grooving exposes or damages structural cord plies, leading to sudden structural carcass failure."
            }
        ]
    },
    {
        "id": "mod-inflation-dynamics",
        "module_code": "MOD-02",
        "title": "Inflation Dynamics, Pressure Retention & Thermal Buildup",
        "category": "MAINTENANCE",
        "estimated_minutes": 8,
        "summary": "Understand cold vs hot pressure measurements, heat dissipation mechanics, and the safety risks of under-inflation.",
        "content_markdown": """# Inflation Dynamics & Thermal Management

### Why Pressure is the Tyre's True Load Carrier
It is not the rubber that carries the weight of the motorcycle and rider — it is the **volume of compressed air** inside the tyre chamber. The rubber carcass merely serves as the pressure vessel.

### Critical Physics: Cold vs. Hot PSI
- **Cold Tyre Pressure:** Pressure measured after the vehicle has been parked for at least 3 hours or driven less than 1.5 km at low speeds.
- **Normal Pressure Rise:** During regular riding, internal air temperature rises, increasing pressure by **2 to 4 PSI**. This is normal and engineered into the tyre's thermal envelope.
- **Warning on 'Bleeding' Hot Tyres:** Never bleed air out of a hot tyre! If you bleed air when the tyre is warm, it will be dangerously under-inflated once it cools down.

### The Danger of Under-Inflation
1. **Excessive Flexing (Hysteresis):** Under-inflated tyres experience extreme sidewall flexing every rotation, generating severe internal heat.
2. **Thermal Carcass Separation:** If internal temperature exceeds 95°C-105°C, the adhesive bonds between rubber compounds and nylon/steel cords degrade, risking sudden tread delamination.
3. **Pinch Flats (Snakebites):** Potholes strike the rim edge directly through the soft tyre profile, slicing the inner tube or puncturing the tubeless bead.

### Inspection Routine for Mechanics
- Always check tyre pressure with an accurate, calibrated dial or digital gauge.
- Inspect the valve core and valve stem rubber for dry rot and micro-cracking.
- Replace the valve cap with a sealing O-ring cap to prevent centrifugal deflation at high rotational speeds.

> **Notice:** General tyre engineering guidance. This material is not a manufacturer endorsement or professional certification.
""",
        "technical_source": "Tyre and Rim Association (TRA) Standards on Inflation Pressure Dynamics",
        "points_reward": 50,
        "quiz_questions": [
            {
                "id": 1,
                "prompt": "When should two-wheeler tyre inflation pressure be measured to ensure accurate baseline readings?",
                "options": [
                    "Immediately after a 50 km high-speed highway trip",
                    "When the tyre is cold (vehicle stationary for at least 3 hours or ridden under 1.5 km)",
                    "Only after submerging the tyre in water",
                    "At midday under direct sunlight"
                ],
                "correct_index": 1,
                "explanation": "Cold pressure readings eliminate thermal expansion variables. Manufacturer specifications are always calibrated for cold tyre temperatures."
            },
            {
                "id": 2,
                "prompt": "If a customer brings in a motorcycle with hot tyres that read 4 PSI above the OEM manual, what should the mechanic do?",
                "options": [
                    "Bleed out the 4 PSI immediately so it matches the manual",
                    "Do not bleed air; thermal pressure rise of 2-4 PSI during riding is normal and expected",
                    "Deflate the tyre completely and pump cold water into the tube",
                    "Advise the rider that the tyre is defective"
                ],
                "correct_index": 1,
                "explanation": "Bleeding air from hot tyres leaves the tyre severely under-inflated once it cools, creating hazardous sidewall flexing and overheating."
            },
            {
                "id": 3,
                "prompt": "What is the primary danger of operating a two-wheeler with persistently low tyre pressure?",
                "options": [
                    "Excessive sidewall flexing causing extreme internal thermal buildup and carcass delamination",
                    "Instantaneous freeze fractures on the tread surface",
                    "Over-spinning the speedometer cable",
                    "Spark plugs fouling"
                ],
                "correct_index": 0,
                "explanation": "Under-inflation increases tyre flex and friction, generating dangerous heat that can melt inner liner bonding and trigger carcass blowouts."
            }
        ]
    },
    {
        "id": "mod-puncture-repair",
        "module_code": "MOD-03",
        "title": "Puncture Damage & Repair Safety (Plugs vs Internal Patches)",
        "category": "SAFETY",
        "estimated_minutes": 12,
        "summary": "Learn the vital distinction between emergency roadside string plugs and permanent internal combi-plug repairs.",
        "content_markdown": """# Puncture Damage & Repair Safety Standards

### Tubeless Tyre Repair: The Vital Distinction
Mechanics in India frequently encounter punctured tubeless tyres. Understanding industry safety standards protects riders from catastrophic failures.

### 1. Temporary Roadside String Plugs (External Wick)
- **What they are:** Rubberized wicks inserted externally using a rasp and insertion needle.
- **Safety Status:** **EMERGENCY TEMPORARY USE ONLY.**
- **Limitations:**
  - They do not seal the inner liner permanently.
  - Water and road salt can penetrate along the cord plies, rusting steel belts or rotting nylon cords.
  - The technician cannot inspect the inside of the tyre for internal carcass scorching or run-flat debris.

### 2. Permanent Professional Repair (Combi-Plug / Mushroom Patch)
- **Standard:** Industry standard (BS AU 159 / RMA guidelines).
- **Procedure:**
  1. Dismount tyre from rim.
  2. Inspect interior for run-flat heat damage (black rubber dust / scorched inner liner).
  3. Ream the injury path straight (max 6 mm diameter).
  4. Buff inner liner, apply chemical vulcanizing cement.
  5. Pull stem through the hole and roll down the rubber patch firmly against the inner liner.
- **Result:** Seals the tread against moisture and seals the inner liner against pressure loss.

### 3. Non-Repairable Damage Areas
- **Sidewall & Shoulder Injuries:** **STRICTLY NON-REPAIRABLE.** The sidewall undergoes continuous dynamic flexion; plugs in this zone blow out under cornering stress.
- **Puncture larger than 6 mm (1/4 inch):** Structural cords are severed; tyre must be decommissioned.
- **Run-Flat Damage:** If the inner liner shows blistering, powdering, or discoloration, the carcass is compromised.

> **Notice:** General safety guidance following British Standard BS AU 159 & RMA industry practices.
""",
        "technical_source": "BS AU 159 & RMA Guidelines for Permanent Pneumatic Tyre Repairs",
        "points_reward": 50,
        "quiz_questions": [
            {
                "id": 1,
                "prompt": "According to professional tyre safety standards, why are external string plugs considered temporary?",
                "options": [
                    "They weigh down the rim and unbalance the wheel",
                    "They do not seal the inner liner from inside and allow moisture to corrode structural plies",
                    "They can only be used on bicycle tyres",
                    "They dissolve in rainwater within 24 hours"
                ],
                "correct_index": 1,
                "explanation": "External string plugs are roadside remedies; without demounting and inspecting the interior liner and applying a vulcanized patch, internal moisture rot and carcass separation can occur."
            },
            {
                "id": 2,
                "prompt": "Which zone of a motorcycle tyre is STRICTLY NON-REPAIRABLE if punctured or cut?",
                "options": [
                    "The central crown tread area within the main grooves",
                    "The sidewall and shoulder flex zone",
                    "The outer rubber strip of the tread within 6mm diameter",
                    "None; every part of a tyre can be patched safely"
                ],
                "correct_index": 1,
                "explanation": "The sidewall undergoes high-frequency flexing during travel. Any plug or patch placed in the sidewall flex zone will dislodge, causing sudden deflation."
            },
            {
                "id": 3,
                "prompt": "What does black rubber powder or dust found inside a demounted tubeless tyre indicate?",
                "options": [
                    "Normal graphite lubricant from the manufacturing plant",
                    "Severe run-flat damage where the tyre was ridden with zero/low air pressure, ruining structural integrity",
                    "High-performance tyre sealant residue",
                    "Evidence of nitrogen gas usage"
                ],
                "correct_index": 1,
                "explanation": "Rubber powder indicates the tyre carcass ground against itself while driven flat. Such tyres are structurally ruined and must be scrapped."
            }
        ]
    },
    {
        "id": "mod-customer-advising",
        "module_code": "MOD-04",
        "title": "Rider Communication & Explaining Inspection Findings",
        "category": "COMMUNICATION",
        "estimated_minutes": 10,
        "summary": "How to translate technical tyre measurements into plain, trust-building safety advice for everyday two-wheeler riders.",
        "content_markdown": """# Transparent Rider Communication & Inspection Guidance

### The Mechanic as the Rider's Safety Advisor
Surveys consistently show that riders trust local mechanics more than advertisements when evaluating two-wheeler maintenance. Clear, transparent communication builds lasting customer loyalty and protects rider safety.

### Principles of Plain-Language Safety Communication
1. **Show, Don't Just Tell:**
   - Point out the physical finding directly on the customer's vehicle (e.g. show the TWI bar or show the depth gauge measurement).
   - Use physical visual comparisons (e.g., comparing 1.2 mm worn tread against 4.0 mm new tread depth).

2. **Differentiate Severity Honestly:**
   - **Green (OK):** Affirm that the tyre has sufficient life; do not create false urgency. Recommend a routine check in 2,000-3,000 km.
   - **Yellow (Monitor):** Advise that the tyre is approaching end-of-life (e.g. 2 mm depth) and should be inspected before the upcoming monsoon season.
   - **Orange / Red (Inspect Soon / Replace Urgently):** Explain the immediate functional hazard (e.g., "Stopping distance in rain doubles when grooves are worn flat; emergency braking will trigger skids").

3. **Digital Record Transparency:**
   - Log the inspection finding in GripWise with rider consent so the rider has an audit trail on their own mobile phone.
   - Transparent records eliminate suspicions of upselling or unnecessary replacements.

> **Notice:** Practical communication principles for independent workshop technicians.
""",
        "technical_source": "Automotive Service Excellence (ASE) & Customer Trust Advisory Guidelines",
        "points_reward": 50,
        "quiz_questions": [
            {
                "id": 1,
                "prompt": "What is the most effective way for a mechanic to communicate tyre wear to a hesitant rider?",
                "options": [
                    "Insist that the tyre is dangerous without showing any measurements",
                    "Show the physical Tread Wear Indicator (TWI) or depth gauge reading directly on the tyre with plain language",
                    "Refuse to service the motorcycle unless the rider buys a new tyre immediately",
                    "Quote complex engineering equations about coefficient of friction"
                ],
                "correct_index": 1,
                "explanation": "Transparent visual proof using standard markers (TWI or depth gauge) demystifies the technical assessment and establishes objective trust."
            },
            {
                "id": 2,
                "prompt": "Why should a mechanic document physical measurements (like tread depth mm and PSI) in digital records?",
                "options": [
                    "To generate automatic fines for the rider",
                    "To create a verifiable history that the rider can review on their phone, reinforcing transparency and safety tracking",
                    "To send confidential vehicle information to advertising agencies",
                    "To increase the cost of simple tyre punctures"
                ],
                "correct_index": 1,
                "explanation": "Documenting verifiable data gives the rider an objective record of wear over time and protects both the rider and mechanic."
            },
            {
                "id": 3,
                "prompt": "If a rider's tyre has 3.5 mm of healthy tread with no cracks or punctures, what is the ethical mechanic action?",
                "options": [
                    "Tell the rider to replace it anyway to boost workshop revenue",
                    "Reassure the rider that the tyre is in good condition, adjust pressure to spec, and schedule a future check",
                    "Claim the tyre is expired because of its brand name",
                    "Recommend puncturing the tyre to install a patch"
                ],
                "correct_index": 1,
                "explanation": "Ethical mechanics never fabricate urgency. Reassuring riders when equipment is safe helps build long-term trust."
            }
        ]
    },
    {
        "id": "mod-safety-ethics",
        "module_code": "MOD-05",
        "title": "Responsible Tyre Recommendations & Safety-First Ethics",
        "category": "ETHICS",
        "estimated_minutes": 15,
        "summary": "Align tyre selection with rider usage, vehicle specs, and safety needs rather than commercial bias.",
        "content_markdown": """# Responsible Recommendations & Professional Ethics

### Core Professional Principle
**A mechanic's first loyalty is to rider safety, mechanical compatibility, and truthful technical advice.**

### 1. Matching Tyre Characteristics to Rider Need
When advising riders on tyre replacement, match the product to their actual operational profile:
- **Daily City Commuters (100cc - 125cc):** Require high puncture resistance, high mileage wear compounds, and reliable wet grip across painted road markings and road debris.
- **Performance & Highway Riders (150cc - 350cc+):** Require directional tread patterns, high-silica wet compounds, cornering stability, and appropriate speed ratings (e.g., P, S, H ratings).
- **Semi-Urban & Rough Road Riders:** Benefit from block-pattern treads that offer traction over unpaved patches, gravel, and wet mud.

### 2. OEM Size and Specification Matching
- Never recommend an oversized 'fat' tyre that compromises handling geometry, causes swingarm fouling, or changes braking balance.
- Always check that the tyre's Load Index and Speed Rating meet or exceed the vehicle manufacturer's specification.

### 3. Ethical Guardrails: Anti-Bias Standards
- **Zero Commission Steering:** Never steer a rider toward an unsuitable tyre size or incompatible compound simply because a brand offers a higher dealer rebate.
- **Transparent Options:** Present the rider with transparent choices based on their budget and riding conditions.
- **GripWise Recognition Rule:** GripWise awards recognition points for educational completion, recorded inspection findings, and customer service quality — **NEVER** for pushing a single brand regardless of customer fit.

> **Notice:** Ethical engineering guidance. GripWise uses transparent, non-coercive professional standards.
""",
        "technical_source": "Society of Automotive Engineers (SAE) Code of Ethics & Tyre Application Safety",
        "points_reward": 50,
        "quiz_questions": [
            {
                "id": 1,
                "prompt": "How does GripWise handle product recommendations and mechanic recognition?",
                "options": [
                    "Mechanics earn double points for pushing a single designated brand regardless of vehicle spec",
                    "Recognition points are awarded for education, recorded findings, and service activity—not for biased brand pushing",
                    "Mechanics are penalized if they recommend any Indian tyre brand",
                    "Points are converted directly into mandatory tyre sales quotas"
                ],
                "correct_index": 1,
                "explanation": "Professional development centers on technical competence and rider safety; rewarding arbitrary brand steering violates consumer trust."
            },
            {
                "id": 2,
                "prompt": "Why should a mechanic avoid recommending an excessively oversized tyre to a commuter motorcycle owner?",
                "options": [
                    "It alters steering geometry, slows turn-in handling, risks swingarm contact, and increases unsprung weight",
                    "Oversized tyres always make the engine quieter",
                    "Commuter motorcycles only support tubed bicycle tyres",
                    "It changes the color of the tyre rubber"
                ],
                "correct_index": 0,
                "explanation": "Oversized tyres distort steering rake and trail, add unsprung weight, risk rubbing against mudguards or drive chains, and degrade safety."
            },
            {
                "id": 3,
                "prompt": "When a daily commuter asks for a replacement tyre recommendation, what primary factors should guide the recommendation?",
                "options": [
                    "Which manufacturer poster is newest in the workshop",
                    "Rider commute distance, road conditions, wet-grip compound needs, and OEM size/speed rating compatibility",
                    "The most expensive racing slick tyre available",
                    "A random coin toss"
                ],
                "correct_index": 1,
                "explanation": "Professional recommendations must evaluate real-world usage patterns, wet road conditions, durability, and exact manufacturer specifications."
            }
        ]
    }
]

SEED_BADGES: List[Dict[str, Any]] = [
    {
        "id": "BADGE_WELCOME",
        "title": "Profile Complete",
        "description": "Completed the workshop profile information checklist.",
        "criteria_description": "Reach 80% or greater profile completeness using accurate workshop details.",
        "icon_name": "badge-check",
        "points_threshold": 0,
        "category": "PROFILE"
    },
    {
        "id": "BADGE_LEARNING_PIONEER",
        "title": "Knowledge Pioneer",
        "description": "Passed your first technical tyre-care educational module.",
        "criteria_description": "Pass any Tyre-Care Learning Hub module quiz with a score of 70% or higher.",
        "icon_name": "book-open",
        "points_threshold": 50,
        "category": "LEARNING"
    },
    {
        "id": "BADGE_TYRE_SCHOLAR",
        "title": "Master Tyre Scholar",
        "description": "Completed all 5 core curriculum modules in the Tyre-Care Learning Hub.",
        "criteria_description": "Successfully pass all 5 educational modules across wear, pressure, repair, communication, and ethics.",
        "icon_name": "award",
        "points_threshold": 250,
        "category": "LEARNING"
    },
    {
        "id": "BADGE_INSPECTION_PRO",
        "title": "Physical Findings Recorder",
        "description": "Recorded measurements during consented physical inspections.",
        "criteria_description": "Record physical findings (tread depth mm and pressure PSI) on 3 or more consented rider inspections.",
        "icon_name": "search",
        "points_threshold": 75,
        "category": "INSPECTION"
    },
    {
        "id": "BADGE_SERVICE_CHAMPION",
        "title": "Service Record Keeper",
        "description": "Recorded completed tyre service work.",
        "criteria_description": "Log 3 or more completed tyre service records (tyre replacements, rotations, puncture repairs).",
        "icon_name": "wrench",
        "points_threshold": 90,
        "category": "SERVICE"
    },
    {
        "id": "BADGE_SAFETY_ADVOCATE",
        "title": "Responsible Recommendations Learner",
        "description": "Completed the learning module on responsible tyre recommendations.",
        "criteria_description": "Complete the 'Responsible Tyre Recommendations' ethics module and attain Silver Tier (100+ points) or above.",
        "icon_name": "shield-check",
        "points_threshold": 100,
        "category": "SAFETY"
    }
]

SEED_INITIATIVES: List[Dict[str, Any]] = [
    {
        "id": "INIT_DIGITAL_GAUGE",
        "title": "Workshop Digital Tread Depth Gauge",
        "category": "TOOL_SUPPORT",
        "description": "A proposed workshop resource for recording physical tread measurements. Final device specifications would need supplier confirmation and validation.",
        "eligibility_level": "BRONZE",
        "status": "PROPOSED_CONCEPT",
        "tool_specs": {
            "tool_type": "Digital tread-depth gauge",
            "specification": "To be confirmed with supplier and validated before use",
        }
    },
    {
        "id": "INIT_CALIBRATED_PRESSURE",
        "title": "Workshop Calibrated Air Pressure Station",
        "category": "TOOL_SUPPORT",
        "description": "A proposed workshop resource for checking tyre pressure. Gauge specifications and any calibration schedule would need supplier confirmation.",
        "eligibility_level": "SILVER",
        "status": "PROPOSED_CONCEPT",
        "tool_specs": {
            "tool_type": "Dial or digital pressure gauge",
            "specification": "To be confirmed with supplier and validated before use",
        }
    },
    {
        "id": "INIT_SAFETY_WALLCHART",
        "title": "Tyre Wear & Safe Riding Diagnostics Wallchart",
        "category": "SAFETY_SIGNAGE",
        "description": "High-durability workshop wallcharts demonstrating motorcycle tread wear patterns, TWI indicators, and wet-braking stopping distances to educate riders during servicing.",
        "eligibility_level": "BRONZE",
        "status": "PROPOSED_CONCEPT",
        "tool_specs": {
            "format": "Weatherproof Vinyl Wall Poster (3ft x 2ft)",
            "languages": "To be selected for the workshop's local community"
        }
    },
    {
        "id": "INIT_TECH_CLINIC",
        "title": "Two-Wheeler Tyre-Care Learning Session",
        "category": "LEARNING_SESSION",
        "description": "A proposed learning session covering tyre construction, tread condition, pressure checks, and safe service practices.",
        "eligibility_level": "GOLD",
        "status": "PROPOSED_CONCEPT",
        "tool_specs": {
            "duration": "To be planned with participating workshops",
            "hands_on_practical": "Format to be agreed"
        }
    }
]

SCORING_RULES = [
    {
        "activity": "Learning Module Completed (Score >= 70%)",
        "points": 50,
        "description": "Pass an educational quiz in the Tyre-Care Learning Hub.",
        "ethical_safeguard": "Points awarded once per module; duplicate quiz attempts do not award duplicate points."
    },
    {
        "activity": "Physical Inspection Findings Recorded",
        "points": 25,
        "description": "Document real tread depth mm, pressure PSI, and diagnostic observations on a rider's inspection.",
        "ethical_safeguard": "Requires active rider consent and real inspection ID; no synthetic entries."
    },
    {
        "activity": "Verified Service Record Logged",
        "points": 30,
        "description": "Record completed maintenance (tyre replacement, rotation, puncture repair) linked to a vehicle.",
        "ethical_safeguard": "Requires rider consent and associated tyre position; auditable service date."
    },
    {
        "activity": "Customer Follow-Up / Referral Completed",
        "points": 20,
        "description": "Successfully complete a consent-confirmed tyre safety follow-up check for a customer.",
        "ethical_safeguard": "Minimal PII retained; customer consent required; no commissions for brand sales."
    }
]
