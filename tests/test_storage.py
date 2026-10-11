"""
test_storage.py - Tests for session state persistence, task toggles, journal, and backup export/import.
"""

import json
from unittest.mock import MagicMock
import pytest
import streamlit as st
from garden_data import GardenProfile, JournalEntry
from recommendation_engine import generate_fallback_plan
import storage


@pytest.fixture(autouse=True)
def clean_session_state():
    """Reset streamlit session state before and after each test."""
    st.session_state.clear()
    storage.init_session_state()
    yield
    st.session_state.clear()


def test_init_session_state():
    """Verify session state defaults are established."""
    assert "soilmate_profile" in st.session_state
    assert "soilmate_plan" in st.session_state
    assert "soilmate_journal" in st.session_state
    assert st.session_state.soilmate_journal == []


def test_profile_and_plan_storage():
    """Verify storing and retrieving profile and generated plan."""
    profile = GardenProfile(
        city_or_region="Chicago",
        garden_type="balcony",
        sunlight="partial_sun",
        space="very_compact",
        goal="herbs",
    )
    storage.set_profile(profile)
    retrieved_profile = storage.get_profile()
    assert retrieved_profile is not None
    assert retrieved_profile.city_or_region == "Chicago"

    plan = generate_fallback_plan(profile)
    storage.set_plan(plan)
    retrieved_plan = storage.get_plan()
    assert retrieved_plan is not None
    assert len(retrieved_plan.seven_day_plan) == 7


def test_toggle_task_completion():
    """Verify toggling tasks marks completion and updates timestamp."""
    profile = GardenProfile(
        city_or_region="Denver",
        garden_type="backyard",
        sunlight="full_sun",
        space="large_beds",
        goal="vegetables",
    )
    plan = generate_fallback_plan(profile)
    storage.set_plan(plan)

    # Initial state
    completed, total = storage.get_completed_tasks_count()
    assert completed == 0
    assert total == 7

    # Mark Day 1 complete
    success = storage.toggle_task(day=1, completed=True)
    assert success
    completed, total = storage.get_completed_tasks_count()
    assert completed == 1

    updated_plan = storage.get_plan()
    task_day1 = updated_plan.seven_day_plan[0]
    assert task_day1.completed is True
    assert task_day1.completed_at is not None

    # Toggle back to False
    storage.toggle_task(day=1, completed=False)
    completed, total = storage.get_completed_tasks_count()
    assert completed == 0


def test_journal_operations():
    """Verify adding, listing, and deleting journal entries."""
    entry1 = JournalEntry(
        id="j1",
        date="2026-10-11",
        observation="Sowed coriander seeds today.",
    )
    entry2 = JournalEntry(
        id="j2",
        date="2026-10-12",
        observation="Soil feels damp, morning sun looks great.",
    )

    storage.add_journal_entry(entry1)
    storage.add_journal_entry(entry2)

    entries = storage.get_journal_entries()
    assert len(entries) == 2

    # Delete j1
    del_res = storage.delete_journal_entry("j1")
    assert del_res is True

    entries_after = storage.get_journal_entries()
    assert len(entries_after) == 1
    assert entries_after[0].id == "j2"


def test_export_and_import_backup_roundtrip():
    """Verify exporting to JSON and restoring from JSON preserves all data."""
    profile = GardenProfile(
        city_or_region="Toronto",
        garden_type="windowsill",
        sunlight="partial_sun",
        space="very_compact",
        goal="herbs",
    )
    plan = generate_fallback_plan(profile)
    storage.set_profile(profile)
    storage.set_plan(plan)
    storage.toggle_task(day=2, completed=True)

    storage.add_journal_entry(
        JournalEntry(id="j_backup", date="2026-10-11", observation="Window sill test")
    )

    # Export
    exported_json = storage.export_state_to_json()
    assert "Toronto" in exported_json
    assert "j_backup" in exported_json

    # Reset
    storage.reset_all_data()
    assert storage.get_profile() is None
    assert storage.get_plan() is None
    assert storage.get_journal_entries() == []

    # Import
    success, msg = storage.import_state_from_json(exported_json)
    assert success is True
    assert storage.get_profile().city_or_region == "Toronto"
    assert storage.get_plan().seven_day_plan[1].completed is True
    assert len(storage.get_journal_entries()) == 1
