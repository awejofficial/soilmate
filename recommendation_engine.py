"""
recommendation_engine.py - Deterministic, rule-based recommendation engine for SoilMate.

Matches user garden profiles with curated horticultural reference data (data/plants.json).
Generates structured 7-day outdoor action plans without external AI dependencies, serving as
both a standalone offline engine and the primary fail-safe fallback.
"""

from __future__ import annotations

from typing import List, Tuple
from garden_data import (
    GardenPlan,
    GardenProfile,
    Plant,
    PlantRecommendation,
    TaskItem,
    load_plants,
)


def score_plant(plant: Plant, profile: GardenProfile) -> Tuple[int, str]:
    """
    Score plant suitability for the given garden profile (0 to 100)
    and return an explanatory rationale string.
    """
    score = 40  # baseline
    reasons: List[str] = []

    # 1. Sunlight compatibility
    if profile.sunlight == plant.preferred_sunlight:
        score += 25
        reasons.append(f"Ideal match for your {profile.sunlight.replace('_', ' ')} exposure")
    elif profile.sunlight in plant.sunlight:
        score += 15
        reasons.append(f"Tolerates your {profile.sunlight.replace('_', ' ')} conditions")
    else:
        score -= 35
        reasons.append(f"Challenging under {profile.sunlight.replace('_', ' ')}")

    # 2. Garden type & space compatibility
    if profile.garden_type in plant.suitable_garden_types:
        score += 15
        reasons.append(f"Well-suited for {profile.garden_type} settings")
    else:
        score -= 20

    if profile.space == "very_compact":
        if plant.space_footprint == "compact":
            score += 20
            reasons.append(f"Compact root footprint fits small pots ({plant.min_container_depth_inches}\" depth)")
        elif plant.space_footprint == "medium":
            score -= 10
            reasons.append("Requires a dedicated medium container")
        else:
            score -= 30
    elif profile.space == "medium_pots":
        if plant.space_footprint in ["compact", "medium"]:
            score += 15
            reasons.append("Fits comfortably in medium planter pots")
    elif profile.space == "large_beds":
        score += 10

    # 3. Goal compatibility
    if profile.goal == "herbs" and plant.category == "herb":
        score += 20
        reasons.append("Matches your culinary herb garden goal")
    elif profile.goal == "vegetables" and plant.category == "vegetable":
        score += 20
        reasons.append("Matches your edible fresh vegetable goal")
    elif profile.goal == "beginner_fast":
        if "25" in plant.days_to_harvest or "20" in plant.days_to_harvest or "30" in plant.days_to_harvest:
            score += 25
            reasons.append(f"Fast harvest time ({plant.days_to_harvest}) gives rapid positive feedback")
        elif plant.difficulty == "beginner":
            score += 15
            reasons.append("Forgiving variety ideal for fast beginner success")
    elif profile.goal == "pollinators_flowers":
        if plant.category == "flower" or "Marigold" in plant.companion_plants:
            score += 25
            reasons.append("Attracts beneficial pollinators and deters pests naturally")

    # 4. Experience level
    if profile.experience_level == "beginner" and plant.difficulty == "beginner":
        score += 10
        reasons.append("Resilient, low-maintenance beginner choice")

    # Clamp score to [0, 100]
    final_score = max(5, min(100, score))
    summary_reason = "; ".join(reasons) if reasons else "Suitable for local growing conditions."
    return final_score, summary_reason


def select_recommended_plants(profile: GardenProfile, top_n: int = 3) -> List[PlantRecommendation]:
    """Select top-scoring candidate plants for a garden profile."""
    all_plants = load_plants()
    scored: List[Tuple[Plant, int, str]] = []

    for plant in all_plants:
        score, reason = score_plant(plant, profile)
        scored.append((plant, score, reason))

    # Sort descending by score
    scored.sort(key=lambda x: x[1], reverse=True)

    # Ensure diversity across categories when possible
    recommendations: List[PlantRecommendation] = []
    seen_categories = set()

    # First pass: pick highest scoring distinct categories
    for plant, score, reason in scored:
        if plant.category not in seen_categories and len(recommendations) < top_n:
            recommendations.append(PlantRecommendation(plant=plant, match_score=score, reason=reason))
            seen_categories.add(plant.category)

    # Second pass: fill remaining slots with highest remaining scores
    for plant, score, reason in scored:
        if len(recommendations) >= top_n:
            break
        if not any(r.plant.id == plant.id for r in recommendations):
            recommendations.append(PlantRecommendation(plant=plant, match_score=score, reason=reason))

    return recommendations


def generate_fallback_plan(profile: GardenProfile) -> GardenPlan:
    """
    Generate a complete, verified 7-day outdoor planting plan using deterministic horticultural logic.
    Used when AI is unavailable, rate-limited, unconfigured, or when deterministic mode is chosen.
    """
    top_picks = select_recommended_plants(profile, top_n=3)
    plant_names = [p.plant.common_name for p in top_picks]
    primary_plant = top_picks[0].plant if top_picks else None

    summary = (
        f"Verified 7-day outdoor planting plan tailored for your {profile.garden_type} "
        f"in {profile.city_or_region} with {profile.sunlight.replace('_', ' ')} exposure. "
        f"Recommended varieties: {', '.join(plant_names)}."
    )

    preparation_steps = [
        f"Select containers with functional bottom drainage holes (minimum depth {primary_plant.min_container_depth_inches}\" for {primary_plant.common_name}).",
        f"Mix well-aerated potting soil: 60% quality potting soil, 25% organic vermicompost, 15% perlite or coco peat.",
        f"Position containers in the outdoor spot receiving at least {primary_plant.min_sunlight_hours} hours of daylight.",
        "Ensure a clean outdoor watering vessel and hand trowel are ready before opening seed packets.",
    ]

    care_instructions = [
        f"Watering: {primary_plant.watering_guidance}",
        f"Soil Health: {primary_plant.soil_preference}",
        f"Outdoor Care Tip: {primary_plant.outdoor_action_tips[0] if primary_plant.outdoor_action_tips else 'Keep soil aerated and weed-free.'}",
        "Screen-Free Habit: Water plants in the morning, touch the topsoil with your bare hand to check moisture, and leave screens inside.",
    ]

    # Generate the 7-day outdoor action tasks (touch grass concept)
    tasks: List[TaskItem] = [
        TaskItem(
            day=1,
            title="Day 1: Outdoor Sunlight & Microclimate Audit",
            instructions=(
                f"Step outside to your {profile.garden_type}. Observe sunlight patterns across your space from morning "
                f"to afternoon. Identify the bright spot that receives direct light for your {plant_names[0]}."
            ),
            estimated_minutes=15,
            completed=False,
            outdoor_tip="Touch grass: Feel the ambient outdoor temperature and check if the spot is shielded from strong winds.",
        ),
        TaskItem(
            day=2,
            title="Day 2: Container Sizing & Drainage Inspection",
            instructions=(
                f"Inspect your pots or planter boxes. Ensure each container has at least 2 unobstructed drainage holes. "
                f"Place a small terracotta shard or mesh over the hole to prevent soil washout. Target depth: {primary_plant.min_container_depth_inches} inches."
            ),
            estimated_minutes=20,
            completed=False,
            outdoor_tip="Pour a splash of water through the empty pot to confirm water flows freely through the drainage holes.",
        ),
        TaskItem(
            day=3,
            title="Day 3: Aerating Soil & Potting Mix Preparation",
            instructions=(
                "Fill pots leaving 1 inch of headspace at the rim. Lightly pre-moisten the potting mix with water until damp "
                "like a wrung-out sponge, but never dripping mud."
            ),
            estimated_minutes=25,
            completed=False,
            outdoor_tip="Dig your fingers 2 inches into the soil. Well-structured potting mix should crumble softly in your palm.",
        ),
        TaskItem(
            day=4,
            title=f"Day 4: Sowing & Planting ({plant_names[0]})",
            instructions=(
                f"Sow seeds or plant seedlings according to verified spacing. For {primary_plant.common_name}, plant shallowly "
                f"(approx 1/4 inch deep). Lightly press soil over the seeds to ensure good seed-to-soil contact."
            ),
            estimated_minutes=30,
            completed=False,
            outdoor_tip=primary_plant.touch_grass_activity,
        ),
        TaskItem(
            day=5,
            title="Day 5: Gentle Bottom Watering & Protective Placement",
            instructions=(
                "Use a gentle spray bottle or watering can rose. Avoid forceful direct streams that dislodge delicate seeds. "
                "Ensure pot sits in bright, gentle outdoor light."
            ),
            estimated_minutes=10,
            completed=False,
            outdoor_tip="Check the soil surface: it should have a dark, damp sheen without pooled standing puddles.",
        ),
        TaskItem(
            day=6,
            title="Day 6: Outdoor Moisture Check & Sprout Watch",
            instructions=(
                "Step outside in the morning without your phone. Press your fingertip 1/2 inch into the pot soil. "
                "If it feels cool and damp, do not water today. Look closely for the first green seedling arches."
            ),
            estimated_minutes=10,
            completed=False,
            outdoor_tip="Take 5 deep breaths in the outdoor morning air before returning inside.",
        ),
        TaskItem(
            day=7,
            title="Day 7: Garden Review, Log First Journal Entry & Weekly Schedule",
            instructions=(
                "Celebrate your first week as a practicing gardener! Inspect all pots, check for signs of growth or weed sprouts, "
                "and record today's notes in your SoilMate journal. Establish a regular morning watering routine for week 2."
            ),
            estimated_minutes=15,
            completed=False,
            outdoor_tip="Gently run your fingers across the foliage or damp soil. You've completed Week 1 of touching grass!",
        ),
    ]

    verification_notes = (
        f"Verified horticultural guidelines sourced from {primary_plant.verification_source}. "
        "Generated deterministically by SoilMate's rule-based engine grounded in curated plant reference data."
    )

    return GardenPlan(
        source="deterministic_fallback",
        provider_label="Deterministic Horticultural Engine (Verified Reference Fallback)",
        model_name="rule-based-horticultural-v1",
        summary=summary,
        profile=profile,
        recommended_plants=top_picks,
        preparation_steps=preparation_steps,
        care_instructions=care_instructions,
        seven_day_plan=tasks,
        verification_notes=verification_notes,
    )
