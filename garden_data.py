"""
garden_data.py - Data schemas and reference plant database loader for SoilMate.

Defines Pydantic models for GardenProfile, Plant, TaskItem, GardenPlan,
and JournalEntry, plus helper functions to load and filter verified plant records.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------

class Plant(BaseModel):
    """Verified horticultural plant profile."""
    id: str
    common_name: str
    scientific_name: str
    category: Literal["herb", "vegetable", "flower"]
    difficulty: Literal["beginner", "intermediate"]
    sunlight: List[Literal["full_sun", "partial_sun", "low_sun_shade"]]
    preferred_sunlight: Literal["full_sun", "partial_sun", "low_sun_shade"]
    min_sunlight_hours: int = Field(ge=1, le=12)
    suitable_garden_types: List[Literal["balcony", "terrace", "backyard", "windowsill"]]
    min_container_depth_inches: int = Field(ge=4, le=36)
    min_container_volume_liters: int = Field(ge=1, le=100)
    space_footprint: Literal["compact", "medium", "large"]
    watering_frequency: str
    watering_guidance: str
    soil_preference: str
    seasonal_guidance: str
    best_planting_months: List[str]
    days_to_germination: str
    days_to_harvest: str
    companion_plants: List[str] = Field(default_factory=list)
    avoid_near: List[str] = Field(default_factory=list)
    outdoor_action_tips: List[str] = Field(default_factory=list)
    touch_grass_activity: str
    verification_source: str


class GardenProfile(BaseModel):
    """User-submitted garden parameters."""
    city_or_region: str = Field(min_length=2, max_length=100)
    garden_type: Literal["balcony", "terrace", "backyard", "windowsill"]
    sunlight: Literal["full_sun", "partial_sun", "low_sun_shade"]
    space: Literal["very_compact", "medium_pots", "large_beds"]
    goal: Literal["herbs", "vegetables", "beginner_fast", "pollinators_flowers"]
    experience_level: Literal["beginner", "intermediate"] = "beginner"
    soil_type: Optional[str] = None
    container_details: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class TaskItem(BaseModel):
    """Individual daily outdoor gardening task for the 7-day checklist."""
    day: int = Field(ge=1, le=7)
    title: str
    instructions: str
    estimated_minutes: int = Field(ge=5, le=120)
    completed: bool = False
    completed_at: Optional[str] = None
    outdoor_tip: str


class PlantRecommendation(BaseModel):
    """Specific plant match included in a generated plan."""
    plant: Plant
    match_score: int = Field(ge=0, le=100)
    reason: str


class GardenPlan(BaseModel):
    """Structured 7-day planting and care plan."""
    source: Literal["ai", "deterministic_fallback"]
    provider_label: str
    model_name: Optional[str] = None
    summary: str
    profile: GardenProfile
    recommended_plants: List[PlantRecommendation]
    preparation_steps: List[str]
    care_instructions: List[str]
    seven_day_plan: List[TaskItem]
    verification_notes: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class JournalEntry(BaseModel):
    """Outdoor gardening log entry recorded by the user."""
    id: str
    date: str
    task_ref: Optional[str] = None
    plant_ref: Optional[str] = None
    observation: str
    growth_stage: Optional[str] = None
    weather_note: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# -----------------------------------------------------------------------------
# Data Loader & Query Helpers
# -----------------------------------------------------------------------------

_PLANTS_CACHE: Optional[List[Plant]] = None


def get_data_file_path() -> Path:
    """Return absolute path to plants.json reference file."""
    return Path(__file__).resolve().parent / "data" / "plants.json"


def load_plants(force_reload: bool = False) -> List[Plant]:
    """Load and validate verified plant profiles from data/plants.json."""
    global _PLANTS_CACHE
    if _PLANTS_CACHE is not None and not force_reload:
        return _PLANTS_CACHE

    data_path = get_data_file_path()
    if not data_path.exists():
        raise FileNotFoundError(f"Plant reference database not found at {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    plants = [Plant.model_validate(item) for item in raw_items]
    _PLANTS_CACHE = plants
    return plants


def get_plant_by_id(plant_id: str) -> Optional[Plant]:
    """Lookup plant by unique ID."""
    for p in load_plants():
        if p.id == plant_id:
            return p
    return None


def filter_plants(
    category: Optional[str] = None,
    sunlight: Optional[str] = None,
    garden_type: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> List[Plant]:
    """Filter plant library by user criteria."""
    results = load_plants()
    if category:
        results = [p for p in results if p.category == category]
    if sunlight:
        results = [p for p in results if sunlight in p.sunlight]
    if garden_type:
        results = [p for p in results if garden_type in p.suitable_garden_types]
    if difficulty:
        results = [p for p in results if p.difficulty == difficulty]
    return results
