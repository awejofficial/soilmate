"""
test_recommendation_engine.py - Tests for deterministic scoring, ranking, and 7-day plan generation.
"""

import pytest
from garden_data import GardenProfile, load_plants
from recommendation_engine import (
    generate_fallback_plan,
    score_plant,
    select_recommended_plants,
)


@pytest.fixture
def sample_balcony_profile():
    return GardenProfile(
        city_or_region="Seattle",
        garden_type="balcony",
        sunlight="partial_sun",
        space="very_compact",
        goal="herbs",
        experience_level="beginner",
    )


@pytest.fixture
def sample_backyard_profile():
    return GardenProfile(
        city_or_region="Austin",
        garden_type="backyard",
        sunlight="full_sun",
        space="large_beds",
        goal="vegetables",
        experience_level="beginner",
    )


def test_score_plant_balcony_herb_matching(sample_balcony_profile):
    """Test that a compact shade-tolerant herb scores higher than a large sun vegetable for a balcony."""
    plants = {p.id: p for p in load_plants()}
    mint = plants["mint"]
    tomato = plants["cherry-tomato"]

    mint_score, mint_reason = score_plant(mint, sample_balcony_profile)
    tomato_score, tomato_reason = score_plant(tomato, sample_balcony_profile)

    assert mint_score > tomato_score
    assert "balcony" in mint_reason.lower() or "partial" in mint_reason.lower()


def test_select_recommended_plants(sample_balcony_profile):
    """Verify top candidates are returned within score bounds and desired count."""
    recs = select_recommended_plants(sample_balcony_profile, top_n=3)
    assert len(recs) == 3
    for r in recs:
        assert 0 <= r.match_score <= 100
        assert len(r.reason) > 5
        assert r.plant is not None


def test_generate_fallback_plan_completeness(sample_balcony_profile):
    """Verify fallback plan meets all PRD requirements for 7-day checklist and verification notes."""
    plan = generate_fallback_plan(sample_balcony_profile)

    assert plan.source == "deterministic_fallback"
    assert "Deterministic" in plan.provider_label
    assert plan.profile.city_or_region == "Seattle"
    assert len(plan.recommended_plants) >= 2
    assert len(plan.preparation_steps) >= 3
    assert len(plan.care_instructions) >= 3
    assert len(plan.seven_day_plan) == 7

    # Validate the 7 days are sequentially numbered and non-empty
    for i, task in enumerate(plan.seven_day_plan, start=1):
        assert task.day == i
        assert f"Day {i}" in task.title
        assert len(task.instructions) > 20
        assert task.estimated_minutes >= 5
        assert not task.completed
        assert len(task.outdoor_tip) > 10

    assert "Royal Horticultural Society" in plan.verification_notes or "verified" in plan.verification_notes.lower()


def test_generate_fallback_plan_backyard(sample_backyard_profile):
    """Verify engine tailors output for vegetable goal in full sun backyard."""
    plan = generate_fallback_plan(sample_backyard_profile)
    plant_names = [r.plant.common_name for r in plan.recommended_plants]

    assert any("Tomato" in name or "Pepper" in name or "Beans" in name for name in plant_names)
    assert plan.seven_day_plan[0].day == 1
    assert len(plan.seven_day_plan) == 7
