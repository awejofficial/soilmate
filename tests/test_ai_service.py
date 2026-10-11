"""
test_ai_service.py - Tests for hosted AI client, prompt grounding, JSON sanitization, and fallback triggers.
"""

import json
from unittest.mock import MagicMock, patch
import pytest
import requests
from garden_data import GardenProfile
from ai_service import (
    _build_ai_prompt,
    _clean_json_response,
    generate_garden_plan,
    get_provider_status,
)
from recommendation_engine import select_recommended_plants


@pytest.fixture
def sample_profile():
    return GardenProfile(
        city_or_region="Portland",
        garden_type="terrace",
        sunlight="full_sun",
        space="medium_pots",
        goal="herbs",
        experience_level="beginner",
    )


def test_provider_status_no_token(monkeypatch):
    """Verify status reports offline/deterministic fallback when no HF_TOKEN is present."""
    monkeypatch.delenv("HF_TOKEN", raising=False)
    status = get_provider_status()

    assert not status["has_token"]
    assert "Rule-Based" in status["mode_description"]
    assert status["configured_model"]


def test_provider_status_with_token(monkeypatch):
    """Verify status reports hosted AI active when HF_TOKEN is provided."""
    monkeypatch.setenv("HF_TOKEN", "hf_test_mock_token_123456")
    status = get_provider_status()

    assert status["has_token"]
    assert "Hosted AI Active" in status["mode_description"]


def test_clean_json_response_markdown_blocks():
    """Verify extraction of JSON wrapped in markdown code blocks."""
    raw_markdown = """Here is your garden plan:
```json
{
  "summary": "Plan summary",
  "selected_plant_ids": ["mint"]
}
```
Happy gardening!"""

    cleaned = _clean_json_response(raw_markdown)
    data = json.loads(cleaned)
    assert data["summary"] == "Plan summary"
    assert data["selected_plant_ids"] == ["mint"]


def test_clean_json_response_raw_braces():
    """Verify extraction when LLM outputs raw JSON with conversational intro."""
    raw_text = 'Sure! {"summary": "Direct json"} Thank you!'
    cleaned = _clean_json_response(raw_text)
    data = json.loads(cleaned)
    assert data["summary"] == "Direct json"


def test_build_ai_prompt_contains_grounded_candidates(sample_profile):
    """Verify prompt embeds user profile parameters and reference catalog candidates."""
    candidate_recs = select_recommended_plants(sample_profile, top_n=3)
    prompt = _build_ai_prompt(sample_profile, candidate_recs)

    assert "Portland" in prompt
    assert "terrace" in prompt
    assert "full sun" in prompt
    assert "Touch Grass" in prompt or "outdoor" in prompt.lower()
    # Ensure verified plant IDs are present
    assert candidate_recs[0].plant.id in prompt


def test_generate_garden_plan_fallback_when_no_token(monkeypatch, sample_profile):
    """Verify missing HF_TOKEN immediately produces deterministic fallback plan without raising exceptions."""
    monkeypatch.delenv("HF_TOKEN", raising=False)
    plan = generate_garden_plan(sample_profile)

    assert plan.source == "deterministic_fallback"
    assert len(plan.seven_day_plan) == 7
    assert len(plan.recommended_plants) >= 2


@patch("requests.post")
def test_generate_garden_plan_fallback_on_api_error(mock_post, monkeypatch, sample_profile):
    """Verify network error or 500 error gracefully degrades to deterministic plan."""
    monkeypatch.setenv("HF_TOKEN", "hf_valid_format_dummy_token_999")
    mock_post.return_value = MagicMock(status_code=500, text="Internal Server Error")

    plan = generate_garden_plan(sample_profile)
    assert plan.source == "deterministic_fallback"
    assert "500" in plan.verification_notes or "unavailable" in plan.verification_notes.lower()
    assert len(plan.seven_day_plan) == 7


@patch("requests.post")
def test_generate_garden_plan_successful_ai_parse(mock_post, monkeypatch, sample_profile):
    """Verify valid AI response is parsed and structured into GardenPlan."""
    monkeypatch.setenv("HF_TOKEN", "hf_valid_format_dummy_token_999")

    mock_ai_content = {
        "summary": "AI tailored terrace garden plan.",
        "selected_plant_ids": ["mint", "basil"],
        "plant_reasons": {
            "mint": "Fast growth in containers",
            "basil": "Loves full sun on the terrace",
        },
        "preparation_steps": ["Inspect drainage", "Mix soil with compost"],
        "care_instructions": ["Water in the morning", "Pinch growing tips"],
        "seven_day_plan": [
            {
                "day": 1,
                "title": "Day 1: Sun Check",
                "instructions": "Measure light on terrace.",
                "estimated_minutes": 15,
                "outdoor_tip": "Touch the sunlight and feel the temperature.",
            },
            {
                "day": 2,
                "title": "Day 2: Pots Ready",
                "instructions": "Check pot drainage holes.",
                "estimated_minutes": 20,
                "outdoor_tip": "Listen to the outdoor breeze.",
            },
            {
                "day": 3,
                "title": "Day 3: Soil Mix",
                "instructions": "Aerate potting soil.",
                "estimated_minutes": 20,
                "outdoor_tip": "Run fingers through soil.",
            },
            {
                "day": 4,
                "title": "Day 4: Plant Mint",
                "instructions": "Plant mint root cutting.",
                "estimated_minutes": 25,
                "outdoor_tip": "Smell the crushed mint leaf.",
            },
            {
                "day": 5,
                "title": "Day 5: Gentle Water",
                "instructions": "Water base of plants.",
                "estimated_minutes": 10,
                "outdoor_tip": "Observe water soaking in.",
            },
            {
                "day": 6,
                "title": "Day 6: Inspect Leaves",
                "instructions": "Look for new shoots.",
                "estimated_minutes": 10,
                "outdoor_tip": "Breathe outdoor air.",
            },
            {
                "day": 7,
                "title": "Day 7: First Harvest Check",
                "instructions": "Log week 1 in journal.",
                "estimated_minutes": 15,
                "outdoor_tip": "Celebrate 7 days outside.",
            },
        ],
        "verification_notes": "Cross-referenced with plant data.",
    }

    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: [{"generated_text": json.dumps(mock_ai_content)}],
    )

    plan = generate_garden_plan(sample_profile)
    assert plan.source == "ai"
    assert "Hosted AI" in plan.provider_label
    assert len(plan.recommended_plants) == 2
    assert plan.recommended_plants[0].plant.id in ["mint", "basil"]
    assert len(plan.seven_day_plan) == 7
    assert plan.seven_day_plan[0].title == "Day 1: Sun Check"
