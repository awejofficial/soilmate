"""
test_plants_data.py - Verification tests for curated horticultural dataset (data/plants.json).
"""

import json
from pathlib import Path
import pytest
from garden_data import (
    Plant,
    filter_plants,
    get_data_file_path,
    get_plant_by_id,
    load_plants,
)


def test_plants_json_file_exists():
    """Verify data/plants.json file is located in the expected directory."""
    path = get_data_file_path()
    assert path.exists(), f"Missing plants.json at {path}"
    assert path.stat().st_size > 500, "plants.json appears truncated or empty"


def test_plants_json_schema_validation():
    """Verify all plants in database conform strictly to the Pydantic Plant schema."""
    plants = load_plants(force_reload=True)
    assert len(plants) >= 12, f"Expected at least 12 curated plants, found {len(plants)}"

    ids = set()
    for plant in plants:
        assert isinstance(plant, Plant)
        assert plant.id, "Plant must have a non-empty id"
        assert plant.id not in ids, f"Duplicate plant ID detected: {plant.id}"
        ids.add(plant.id)

        assert plant.common_name, "Plant must have a common name"
        assert plant.scientific_name, "Plant must have a scientific name"
        assert plant.category in ["herb", "vegetable", "flower"]
        assert plant.difficulty in ["beginner", "intermediate"]
        assert len(plant.sunlight) > 0, "Plant must specify at least one sunlight condition"
        assert plant.min_sunlight_hours >= 1
        assert plant.min_container_depth_inches >= 4
        assert plant.min_container_volume_liters >= 1
        assert len(plant.outdoor_action_tips) > 0, "Plant must have outdoor action tips"
        assert plant.touch_grass_activity, "Plant must have a touch grass activity"
        assert plant.verification_source, "Plant must cite verification source"


def test_get_plant_by_id():
    """Verify ID lookup returns correct plant and None for invalid IDs."""
    basil = get_plant_by_id("basil")
    assert basil is not None
    assert basil.common_name == "Sweet Basil"
    assert basil.category == "herb"

    mint = get_plant_by_id("mint")
    assert mint is not None
    assert "Mentha" in mint.scientific_name

    non_existent = get_plant_by_id("dragon_fruit_super_rare_999")
    assert non_existent is None


def test_filter_plants():
    """Verify catalog filtering by category, sunlight, and difficulty."""
    herbs = filter_plants(category="herb")
    assert len(herbs) >= 3
    assert all(p.category == "herb" for p in herbs)

    veggies = filter_plants(category="vegetable")
    assert len(veggies) >= 3
    assert all(p.category == "vegetable" for p in veggies)

    full_sun = filter_plants(sunlight="full_sun")
    assert len(full_sun) >= 5
    assert all("full_sun" in p.sunlight for p in full_sun)

    beginner = filter_plants(difficulty="beginner")
    assert len(beginner) >= 5
    assert all(p.difficulty == "beginner" for p in beginner)
