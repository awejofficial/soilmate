"""
storage.py - Session state management, local persistence, and backup import/export for SoilMate.

Manages in-memory Streamlit state, task completion tracking, journal entries,
and portable JSON export/import ensuring zero cloud dependency or optional Supabase sync.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import streamlit as st

from garden_data import GardenPlan, GardenProfile, JournalEntry


def init_session_state() -> None:
    """Initialize default keys in st.session_state if not already present."""
    if "soilmate_profile" not in st.session_state:
        st.session_state.soilmate_profile = None

    if "soilmate_plan" not in st.session_state:
        st.session_state.soilmate_plan = None

    if "soilmate_journal" not in st.session_state:
        st.session_state.soilmate_journal = []

    if "outdoor_mode_active" not in st.session_state:
        st.session_state.outdoor_mode_active = False

    if "notification_message" not in st.session_state:
        st.session_state.notification_message = None


def get_profile() -> Optional[GardenProfile]:
    """Retrieve active garden profile."""
    return st.session_state.get("soilmate_profile")


def set_profile(profile: GardenProfile) -> None:
    """Save active garden profile."""
    st.session_state.soilmate_profile = profile


def get_plan() -> Optional[GardenPlan]:
    """Retrieve active 7-day garden plan."""
    return st.session_state.get("soilmate_plan")


def set_plan(plan: GardenPlan) -> None:
    """Save active 7-day garden plan."""
    st.session_state.soilmate_plan = plan


def toggle_task(day: int, completed: bool) -> bool:
    """
    Toggle completion status of a day's task.
    Returns True if task was found and updated, False otherwise.
    """
    plan: Optional[GardenPlan] = st.session_state.get("soilmate_plan")
    if not plan:
        return False

    for task in plan.seven_day_plan:
        if task.day == day:
            task.completed = completed
            task.completed_at = datetime.now().isoformat() if completed else None
            st.session_state.soilmate_plan = plan
            return True
    return False


def get_completed_tasks_count() -> Tuple[int, int]:
    """Return tuple of (completed_count, total_count) for the 7-day plan."""
    plan: Optional[GardenPlan] = st.session_state.get("soilmate_plan")
    if not plan or not plan.seven_day_plan:
        return 0, 7
    completed = sum(1 for t in plan.seven_day_plan if t.completed)
    return completed, len(plan.seven_day_plan)


def get_journal_entries() -> List[JournalEntry]:
    """Return list of user's journal entries sorted by newest first."""
    entries: List[JournalEntry] = st.session_state.get("soilmate_journal", [])
    return sorted(entries, key=lambda e: e.created_at, reverse=True)


def add_journal_entry(entry: JournalEntry) -> None:
    """Add a new journal entry."""
    if "soilmate_journal" not in st.session_state:
        st.session_state.soilmate_journal = []
    st.session_state.soilmate_journal.append(entry)


def delete_journal_entry(entry_id: str) -> bool:
    """Delete a journal entry by ID."""
    entries: List[JournalEntry] = st.session_state.get("soilmate_journal", [])
    filtered = [e for e in entries if e.id != entry_id]
    if len(filtered) != len(entries):
        st.session_state.soilmate_journal = filtered
        return True
    return False


def reset_all_data() -> None:
    """Clear all session state data."""
    st.session_state.soilmate_profile = None
    st.session_state.soilmate_plan = None
    st.session_state.soilmate_journal = []
    st.session_state.outdoor_mode_active = False


def export_state_to_json() -> str:
    """Export complete garden data as a formatted JSON string for backup."""
    profile = get_profile()
    plan = get_plan()
    journal = get_journal_entries()

    data: Dict[str, Any] = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "profile": profile.model_dump() if profile else None,
        "plan": plan.model_dump() if plan else None,
        "journal": [entry.model_dump() for entry in journal],
    }
    return json.dumps(data, indent=2)


def import_state_from_json(json_str: str) -> Tuple[bool, str]:
    """
    Import and validate garden data from JSON string backup.
    Returns (success: bool, message: str).
    """
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            return False, "Invalid backup format: root must be a JSON object."

        if data.get("profile"):
            profile = GardenProfile.model_validate(data["profile"])
            set_profile(profile)
        else:
            st.session_state.soilmate_profile = None

        if data.get("plan"):
            plan = GardenPlan.model_validate(data["plan"])
            set_plan(plan)
        else:
            st.session_state.soilmate_plan = None

        if data.get("journal"):
            entries = [JournalEntry.model_validate(e) for e in data["journal"]]
            st.session_state.soilmate_journal = entries
        else:
            st.session_state.soilmate_journal = []

        return True, "Garden data imported successfully!"
    except Exception as e:
        return False, f"Failed to import backup: {str(e)}"
