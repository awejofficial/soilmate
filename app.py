"""
app.py - Main Streamlit web application for SoilMate.

SoilMate — Grow More. Scroll Less.
An open-source AI gardening assistant designed to help beginners transform
gardening aspirations into verified outdoor actions.
"""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime
import streamlit as st

from garden_data import (
    GardenPlan,
    GardenProfile,
    JournalEntry,
    Plant,
    filter_plants,
    load_plants,
)
from recommendation_engine import generate_fallback_plan
from ai_service import generate_garden_plan, get_provider_status
import storage

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="SoilMate — Grow More. Scroll Less.",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Custom Styling (Organic Earthy Design System)
# -----------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
/* -------------------------------------------------------------------------
   SoilMate Earthy Natural Theme
   Forest Green: #2D5A27 | Terracotta: #C86D51 | Sage: #527A52 | Sand: #FAF8F5
   Dark Soil: #1F291E   | Cream Border: #E5DFC5
------------------------------------------------------------------------- */

:root {
    --forest-green: #2D5A27;
    --forest-green-dark: #1E3F1A;
    --terracotta: #C86D51;
    --terracotta-hover: #B2583D;
    --sage: #527A52;
    --sage-light: #EBF2EB;
    --sand-bg: #FAF8F5;
    --soil-dark: #1F291E;
    --card-border: #E8E2D9;
}

/* Base Body Adjustments */
.stApp {
    background-color: var(--sand-bg);
    color: var(--soil-dark);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Main Hero Banner */
.soilmate-hero {
    background: linear-gradient(135deg, #2D5A27 0%, #1F3F1A 100%);
    color: #FFFFFF !important;
    padding: 2.2rem 2.5rem;
    border-radius: 14px;
    margin-bottom: 1.8rem;
    box-shadow: 0 4px 14px rgba(31, 41, 30, 0.12);
}
.soilmate-hero h1 {
    color: #FFFFFF !important;
    font-size: 2.3rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
}
.soilmate-hero p {
    color: #E2ECD8 !important;
    font-size: 1.15rem;
    margin-bottom: 0;
}

/* Stat & Badge Pills */
.status-pill {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.3px;
    margin-right: 0.5rem;
}
.status-pill-ai {
    background-color: #E8F5E9;
    color: #1B5E20;
    border: 1px solid #A5D6A7;
}
.status-pill-deterministic {
    background-color: #FFF3E0;
    color: #E65100;
    border: 1px solid #FFE082;
}

/* Card Styling */
.garden-card {
    background: #FFFFFF;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.3rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.garden-card:hover {
    box-shadow: 0 4px 12px rgba(45, 90, 39, 0.08);
}
.garden-card h4 {
    color: var(--forest-green);
    margin-top: 0;
    margin-bottom: 0.5rem;
    font-size: 1.2rem;
}

/* Outdoor Mode Special View */
.outdoor-hero-card {
    background: linear-gradient(135deg, #1F3F1A 0%, #152B12 100%);
    color: #FFFFFF !important;
    padding: 2.5rem;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    margin-bottom: 1.5rem;
}
.outdoor-hero-card h2 {
    color: #FFFFFF !important;
    font-size: 2.2rem;
    margin-bottom: 0.8rem;
}
.outdoor-hero-card p {
    color: #D4E7CE !important;
    font-size: 1.25rem;
    line-height: 1.6;
}
.outdoor-touch-grass-box {
    background-color: #EBF3E8;
    border-left: 4px solid var(--forest-green);
    padding: 1rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin: 0.8rem 0;
    font-size: 0.95rem;
    color: #244120;
}

/* Big Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
}

/* Custom highlight tags */
.tag-badge {
    display: inline-block;
    background-color: #F0EFEA;
    color: #4A4A48;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------

storage.init_session_state()
provider_status = get_provider_status()


# -----------------------------------------------------------------------------
# Sidebar Navigation & Outdoor Mode Toggle
# -----------------------------------------------------------------------------

with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=300&auto=format&fit=crop&q=80",
        caption="SoilMate — Grow More. Scroll Less.",
        use_container_width=True,
    )

    st.markdown("### 🌿 SoilMate Navigator")

    # Mode Selector
    app_view = st.radio(
        "Select View",
        [
            "🌱 Garden Planner",
            "📋 7-Day Outdoor Plan",
            "☀️ Outdoor Mode",
            "📖 Garden Journal",
            "🌿 Plant Library",
            "⚙️ Settings & Backup",
        ],
        index=2 if st.session_state.outdoor_mode_active else 0,
        key="navigation_view_radio",
    )

    st.markdown("---")

    # Provider Status Badge
    if provider_status["has_token"]:
        st.markdown(
            f"""
            <div class="status-pill status-pill-ai">
                ✨ Cloud AI Active<br>
                <small>{provider_status['configured_model']}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="status-pill status-pill-deterministic">
                🛡️ Verified Fallback Engine<br>
                <small>Deterministic & Offline-Ready</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Checklist Progress in Sidebar
    active_plan = storage.get_plan()
    if active_plan:
        completed, total = storage.get_completed_tasks_count()
        progress_pct = int((completed / total) * 100) if total > 0 else 0
        st.markdown(f"**Checklist Progress: {completed}/{total} Days**")
        st.progress(progress_pct / 100.0)
        st.caption(f"{progress_pct}% of outdoor tasks completed")
    else:
        st.caption("No garden plan generated yet. Fill out the intake form to get started!")

    st.markdown("---")
    st.caption("Hacktoberfest 2026 DEV Challenge: Week 1 — Touch Grass 🌱")


# -----------------------------------------------------------------------------
# VIEW 1: GARDEN PLANNER
# -----------------------------------------------------------------------------

if app_view == "🌱 Garden Planner":
    st.markdown(
        """
        <div class="soilmate-hero">
            <h1>🌱 Plan Your Outdoor Garden</h1>
            <p>Tell SoilMate about your space, sunlight, and goals. Receive an actionable 7-day outdoor action plan backed by verified horticultural facts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_form, col_info = st.columns([1.1, 0.9], gap="large")

    with col_form:
        st.subheader("1. Your Garden Profile")
        with st.form("garden_profile_form", clear_on_submit=False):
            city_or_region = st.text_input(
                "City or Region",
                value="Bangalore" if not storage.get_profile() else storage.get_profile().city_or_region,
                placeholder="e.g. Austin, London, Bangalore, Melbourne",
                help="Used to tailor regional climate and seasonal planting guidance.",
            )

            garden_type = st.selectbox(
                "Garden Space Type",
                options=["balcony", "terrace", "backyard", "windowsill"],
                format_func=lambda x: {
                    "balcony": "Balcony (Pots & Railing Planters)",
                    "terrace": "Terrace / Rooftop Garden",
                    "backyard": "Backyard / In-Ground Beds",
                    "windowsill": "Windowsill (Small Pots)",
                }[x],
            )

            sunlight = st.selectbox(
                "Daily Sunlight Availability",
                options=["full_sun", "partial_sun", "low_sun_shade"],
                format_func=lambda x: {
                    "full_sun": "Full Sun (6+ hours direct sunlight)",
                    "partial_sun": "Partial Sun (3 to 5 hours direct sun)",
                    "low_sun_shade": "Low Sun / Bright Shade (< 3 hours)",
                }[x],
            )

            space = st.selectbox(
                "Available Space Footprint",
                options=["very_compact", "medium_pots", "large_beds"],
                format_func=lambda x: {
                    "very_compact": "Very Compact (1 - 2 small containers)",
                    "medium_pots": "Medium Space (3 - 5 medium pots)",
                    "large_beds": "Large Space (Multiple large beds/troughs)",
                }[x],
            )

            goal = st.selectbox(
                "Primary Gardening Goal",
                options=["herbs", "vegetables", "beginner_fast", "pollinators_flowers"],
                format_func=lambda x: {
                    "herbs": "Culinary Fresh Herbs (Basil, Mint, Coriander)",
                    "vegetables": "Edible Vegetables & Greens (Spinach, Tomatoes, Peppers)",
                    "beginner_fast": "Quick Beginner Wins (Methi, Radish, Scallions)",
                    "pollinators_flowers": "Pollinators & Companion Blooms (Marigold)",
                }[x],
            )

            experience_level = st.select_slider(
                "Your Experience Level",
                options=["beginner", "intermediate"],
                value="beginner",
            )

            notes = st.text_input(
                "Optional Details (Containers, soil, or specific preferences)",
                placeholder="e.g. 10-inch terracotta pots with organic potting mix",
            )

            submit_plan = st.form_submit_button("🌱 Generate My 7-Day Outdoor Plan", use_container_width=True)

        if submit_plan:
            if not city_or_region.strip():
                st.error("Please enter your city or region.")
            else:
                profile = GardenProfile(
                    city_or_region=city_or_region.strip(),
                    garden_type=garden_type,
                    sunlight=sunlight,
                    space=space,
                    goal=goal,
                    experience_level=experience_level,
                    container_details=notes.strip() if notes else None,
                )
                storage.set_profile(profile)

                with st.spinner("Analyzing verified plant references and building your outdoor schedule..."):
                    new_plan = generate_garden_plan(profile)
                    storage.set_plan(new_plan)
                st.success("Your customized 7-day plan is ready!")
                st.rerun()

    with col_info:
        st.subheader("2. How SoilMate Works")
        st.markdown(
            """
            <div class="garden-card">
                <h4>🎯 Zero Screen-Time Traps</h4>
                <p>Most gardening apps keep you glued to your phone reading forums. SoilMate does the opposite: it gives you <strong>one crisp outdoor action per day</strong> so you can put your phone down and touch soil.</p>
            </div>
            <div class="garden-card">
                <h4>🛡️ Verified Horticultural Grounding</h4>
                <p>Every plant recommendation is cross-referenced with university extension guides and botanical records. No hallucinated watering schedules or impossible companion plants.</p>
            </div>
            <div class="garden-card">
                <h4>⚡ Free-Tier & Resilient</h4>
                <p>Works effortlessly on free hosting. If hosted AI is unavailable or rate-limited, our deterministic horticultural engine activates automatically with zero disruption.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Display Generated Plan if present
    plan = storage.get_plan()
    if plan:
        st.markdown("---")
        st.subheader("🌿 Your Generated Gardening Plan")

        source_badge = (
            f'<span class="status-pill status-pill-ai">✨ Generated by {plan.provider_label}</span>'
            if plan.source == "ai"
            else f'<span class="status-pill status-pill-deterministic">🛡️ {plan.provider_label}</span>'
        )
        st.markdown(source_badge, unsafe_allow_html=True)

        st.info(f"**Plan Summary:** {plan.summary}")

        st.markdown("### Recommended Varieties For Your Space")
        rec_cols = st.columns(len(plan.recommended_plants))
        for idx, rec in enumerate(plan.recommended_plants):
            with rec_cols[idx]:
                p = rec.plant
                st.markdown(
                    f"""
                    <div class="garden-card">
                        <h4>{p.common_name}</h4>
                        <p style="font-style: italic; color: #555; font-size: 0.9rem;">{p.scientific_name}</p>
                        <div>
                            <span class="tag-badge">☀️ {p.preferred_sunlight.replace('_', ' ')}</span>
                            <span class="tag-badge">🪴 Min {p.min_container_depth_inches}" depth</span>
                            <span class="tag-badge">⏱️ {p.days_to_harvest}</span>
                        </div>
                        <p style="margin-top: 0.6rem; font-size: 0.9rem;"><strong>Why this plant:</strong> {rec.reason}</p>
                        <p style="font-size: 0.85rem; color: #333;"><strong>Watering:</strong> {p.watering_frequency}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        col_prep, col_care = st.columns(2)
        with col_prep:
            st.markdown("#### 🛠️ Preparation Steps")
            for step in plan.preparation_steps:
                st.markdown(f"- {step}")
        with col_care:
            st.markdown("#### 💧 Essential Care Guidelines")
            for care in plan.care_instructions:
                st.markdown(f"- {care}")

        st.caption(f"ℹ️ {plan.verification_notes}")


# -----------------------------------------------------------------------------
# VIEW 2: 7-DAY OUTDOOR CHECKLIST
# -----------------------------------------------------------------------------

elif app_view == "📋 7-Day Outdoor Plan":
    st.markdown(
        """
        <div class="soilmate-hero">
            <h1>📋 7-Day Outdoor Action Checklist</h1>
            <p>One focused outdoor activity per day. Step outside, touch grass, and observe your garden.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    plan = storage.get_plan()
    if not plan:
        st.warning("You haven't generated a garden plan yet! Go to the '🌱 Garden Planner' tab to create one.")
    else:
        completed, total = storage.get_completed_tasks_count()
        progress_pct = int((completed / total) * 100) if total > 0 else 0

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        col_metric1.metric("Tasks Completed", f"{completed} / {total}")
        col_metric2.metric("Completion Rate", f"{progress_pct}%")
        col_metric3.metric("Goal", "Touch Grass Every Day 🌱")

        st.progress(progress_pct / 100.0)

        # Quick Outdoor Mode CTA
        st.markdown(
            """
            <div style="background-color: #EBF3E8; border: 1px solid #C4DFC0; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <h4 style="color: #2D5A27; margin:0 0 0.4rem 0;">📱 Taking your phone outside?</h4>
                <p style="margin: 0; color: #2D5A27;">Switch to <strong>Outdoor Mode</strong> for high-contrast, distraction-free outdoor instructions with zero digital clutter.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Daily Outdoor Tasks")
        for task in plan.seven_day_plan:
            with st.container():
                checked = st.checkbox(
                    f"**{task.title}** (Estimated: ~{task.estimated_minutes} min)",
                    value=task.completed,
                    key=f"task_check_{task.day}",
                )
                if checked != task.completed:
                    storage.toggle_task(task.day, checked)
                    st.rerun()

                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{task.instructions}")
                st.markdown(
                    f"""
                    <div class="outdoor-touch-grass-box" style="margin-left: 1.5rem;">
                        <strong>🌿 Touch Grass Action:</strong> {task.outdoor_tip}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if task.completed and task.completed_at:
                    st.markdown(
                        f"&nbsp;&nbsp;&nbsp;&nbsp;<small style='color: #2D5A27;'>✅ Completed at: {task.completed_at[:16].replace('T', ' ')}</small>",
                        unsafe_allow_html=True,
                    )
                st.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #ECE7DE;'>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 3: OUTDOOR MODE (DISTRACTION-FREE TOUCH GRASS VIEW)
# -----------------------------------------------------------------------------

elif app_view == "☀️ Outdoor Mode":
    plan = storage.get_plan()
    if not plan:
        st.info("Please create a plan first under '🌱 Garden Planner' to use Outdoor Mode.")
    else:
        # Find first incomplete task
        next_task = next((t for t in plan.seven_day_plan if not t.completed), None)

        st.markdown(
            """
            <div class="outdoor-hero-card">
                <h2>☀️ Outdoor Mode: Focus & Touch Grass</h2>
                <p>No feeds. No rabbit holes. Just sunlight, fresh air, and your plants.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if next_task:
            st.markdown(
                f"""
                <div class="garden-card" style="border: 2px solid #2D5A27; padding: 2rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="status-pill status-pill-ai" style="font-size: 1rem; padding: 0.4rem 1.2rem;">
                            🎯 Next Action: Day {next_task.day}
                        </span>
                        <span style="font-weight: 600; color: #666;">⏱️ ~{next_task.estimated_minutes} Minutes</span>
                    </div>
                    <h3 style="color: #2D5A27; font-size: 1.8rem; margin-top: 1rem;">{next_task.title}</h3>
                    <p style="font-size: 1.2rem; line-height: 1.7; color: #1F291E; margin-top: 1rem;">
                        {next_task.instructions}
                    </p>
                    <div class="outdoor-touch-grass-box" style="font-size: 1.1rem; padding: 1.2rem; margin: 1.5rem 0;">
                        <strong>🌿 Touch Grass Activity:</strong><br>{next_task.outdoor_tip}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_done, col_quick_log = st.columns([1, 1])
            with col_done:
                if st.button("✅ Mark Day Done & Put Phone Away", use_container_width=True, type="primary"):
                    storage.toggle_task(next_task.day, True)
                    # Automatically log a journal stub
                    storage.add_journal_entry(
                        JournalEntry(
                            id=str(uuid.uuid4())[:8],
                            date=date.today().isoformat(),
                            task_ref=next_task.title,
                            observation="Completed outdoor task outdoors. Checked soil moisture and light.",
                        )
                    )
                    st.balloons()
                    st.success(f"Day {next_task.day} marked complete! Step into the sun and enjoy your garden.")
                    st.rerun()

            with col_quick_log:
                quick_note = st.text_input("Quick Outdoor Observation (Optional)", placeholder="e.g. Soil feels damp, spotted tiny sprout")
                if st.button("📝 Save Quick Note", use_container_width=True):
                    if quick_note.strip():
                        storage.add_journal_entry(
                            JournalEntry(
                                id=str(uuid.uuid4())[:8],
                                date=date.today().isoformat(),
                                task_ref=next_task.title,
                                observation=quick_note.strip(),
                            )
                        )
                        st.success("Observation saved to your Garden Journal!")
                        st.rerun()
        else:
            st.markdown(
                """
                <div class="garden-card" style="text-align: center; padding: 3rem;">
                    <h2 style="color: #2D5A27;">🎉 All 7 Days Completed!</h2>
                    <p style="font-size: 1.2rem; color: #444;">
                        Congratulations! You have completed your 7-day outdoor gardening challenge.
                        You've built hands-on outdoor habits and given your plants the care they need.
                    </p>
                    <p style="font-size: 1rem; color: #666;">
                        Continue checking in with your Garden Journal to track ongoing growth.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# -----------------------------------------------------------------------------
# VIEW 4: GARDEN JOURNAL
# -----------------------------------------------------------------------------

elif app_view == "📖 Garden Journal":
    st.markdown(
        """
        <div class="soilmate-hero">
            <h1>📖 Garden Journal</h1>
            <p>Record outdoor observations, soil dampness, first sprouts, and weather notes. Kept private and locally available.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_add, col_list = st.columns([1, 1.2], gap="large")

    with col_add:
        st.subheader("Add Journal Entry")
        with st.form("add_journal_form", clear_on_submit=True):
            entry_date = st.date_input("Date", value=date.today())
            task_ref = st.selectbox(
                "Associated Task (Optional)",
                options=["None"] + [f"Day {i}" for i in range(1, 8)],
            )
            plant_ref = st.text_input("Plant Observed (Optional)", placeholder="e.g. Sweet Basil")
            growth_stage = st.selectbox(
                "Growth Stage",
                options=["Seed sowing", "Germination / Sprout", "Vegetative growth", "Flowering", "Harvest ready"],
            )
            weather_note = st.text_input("Weather (Optional)", placeholder="e.g. Sunny 26°C, gentle breeze")
            observation = st.text_area("What did you observe outdoors?", placeholder="Describe soil texture, seedling height, or scent...", height=120)

            submit_entry = st.form_submit_button("🌿 Save Journal Entry", use_container_width=True)

        if submit_entry:
            if not observation.strip():
                st.error("Please add an observation note.")
            else:
                entry = JournalEntry(
                    id=str(uuid.uuid4())[:8],
                    date=entry_date.isoformat(),
                    task_ref=task_ref if task_ref != "None" else None,
                    plant_ref=plant_ref.strip() if plant_ref else None,
                    growth_stage=growth_stage,
                    weather_note=weather_note.strip() if weather_note else None,
                    observation=observation.strip(),
                )
                storage.add_journal_entry(entry)
                st.success("Entry added to your journal!")
                st.rerun()

    with col_list:
        st.subheader("Your Past Observations")
        entries = storage.get_journal_entries()
        if not entries:
            st.info("No journal entries logged yet. Complete today's outdoor task and record your first observation!")
        else:
            for entry in entries:
                with st.container():
                    st.markdown(
                        f"""
                        <div class="garden-card">
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <strong style="color: #2D5A27;">📅 {entry.date}</strong>
                                <span style="font-size: 0.85rem; color: #777;">{entry.growth_stage or ''}</span>
                            </div>
                            <p style="margin: 0.6rem 0; font-size: 1rem; color: #1F291E;">{entry.observation}</p>
                            <div>
                                {f'<span class="tag-badge">🌱 {entry.plant_ref}</span>' if entry.plant_ref else ''}
                                {f'<span class="tag-badge">📋 {entry.task_ref}</span>' if entry.task_ref else ''}
                                {f'<span class="tag-badge">☀️ {entry.weather_note}</span>' if entry.weather_note else ''}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("🗑️ Delete Entry", key=f"del_{entry.id}"):
                        storage.delete_journal_entry(entry.id)
                        st.rerun()


# -----------------------------------------------------------------------------
# VIEW 5: PLANT LIBRARY
# -----------------------------------------------------------------------------

elif app_view == "🌿 Plant Library":
    st.markdown(
        """
        <div class="soilmate-hero">
            <h1>🌿 Curated Plant Reference Catalog</h1>
            <p>Browse 15 verified varieties with scientifically verified sunlight, container, and care guidelines.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        cat_filter = st.selectbox("Filter by Category", ["All", "herb", "vegetable", "flower"])
    with col_filter2:
        sun_filter = st.selectbox("Filter by Sunlight", ["All", "full_sun", "partial_sun", "low_sun_shade"])
    with col_filter3:
        diff_filter = st.selectbox("Filter by Difficulty", ["All", "beginner", "intermediate"])

    plants = filter_plants(
        category=None if cat_filter == "All" else cat_filter,
        sunlight=None if sun_filter == "All" else sun_filter,
        difficulty=None if diff_filter == "All" else diff_filter,
    )

    st.markdown(f"**Showing {len(plants)} verified plant species:**")

    for plant in plants:
        with st.expander(f"🌱 {plant.common_name} ({plant.scientific_name}) — {plant.category.title()}"):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown(f"**Preferred Sunlight:** {plant.preferred_sunlight.replace('_', ' ').title()} (Min {plant.min_sunlight_hours} hrs)")
                st.markdown(f"**Min Container Depth:** {plant.min_container_depth_inches} inches ({plant.min_container_volume_liters}L volume)")
                st.markdown(f"**Days to Harvest:** {plant.days_to_harvest}")
                st.markdown(f"**Difficulty:** {plant.difficulty.title()}")
                st.markdown(f"**Watering Guidance:** {plant.watering_guidance}")
            with col_p2:
                st.markdown(f"**Soil Preference:** {plant.soil_preference}")
                st.markdown(f"**Seasonal Window:** {plant.seasonal_guidance}")
                st.markdown(f"**Companion Plants:** {', '.join(plant.companion_plants) if plant.companion_plants else 'None'}")
                st.markdown(f"**Touch Grass Tip:** {plant.touch_grass_activity}")
                st.caption(f"Source: {plant.verification_source}")


# -----------------------------------------------------------------------------
# VIEW 6: SETTINGS & BACKUP
# -----------------------------------------------------------------------------

elif app_view == "⚙️ Settings & Backup":
    st.markdown(
        """
        <div class="soilmate-hero">
            <h1>⚙️ Settings & Data Control</h1>
            <p>Inspect AI configuration, export portable backups, and manage your data with complete privacy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_set1, col_set2 = st.columns(2, gap="large")

    with col_set1:
        st.subheader("1. AI Inference Configuration")
        st.markdown(
            f"""
            <div class="garden-card">
                <p><strong>Provider:</strong> {provider_status['provider']}</p>
                <p><strong>Configured Model:</strong> <code>{provider_status['configured_model']}</code></p>
                <p><strong>Request Timeout:</strong> {provider_status['timeout_seconds']} seconds</p>
                <p><strong>Active Status:</strong> {provider_status['mode_description']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Cloud Deployment Setup (Streamlit Secrets)")
        st.markdown(
            """
            To activate hosted AI on Streamlit Community Cloud:
            1. Open your Streamlit Cloud app settings.
            2. Navigate to **Secrets**.
            3. Add your Hugging Face User Access Token:
            ```toml
            HF_TOKEN = "hf_your_token_here"
            AI_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
            REQUEST_TIMEOUT_SECONDS = 30
            ```
            If no token is supplied, SoilMate seamlessly uses its **Deterministic Horticultural Engine** at ₹0 cost.
            """
        )

    with col_set2:
        st.subheader("2. Backup & Portability")
        backup_json_str = storage.export_state_to_json()

        st.download_button(
            label="💾 Download Backup (JSON)",
            data=backup_json_str,
            file_name=f"soilmate_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption("Exports your profile, current 7-day checklist progress, and all journal entries.")

        st.markdown("#### Restore From Backup")
        uploaded_backup = st.file_uploader("Upload backup JSON file", type=["json"])
        if uploaded_backup is not None:
            content = uploaded_backup.read().decode("utf-8")
            if st.button("📥 Import Backup Now", use_container_width=True):
                success, msg = storage.import_state_from_json(content)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")
        st.subheader("3. Reset Application")
        if st.button("⚠️ Reset All Garden Data", type="secondary", use_container_width=True):
            storage.reset_all_data()
            st.warning("All garden data and journal entries have been reset.")
            st.rerun()


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------

st.markdown(
    """
    <div style="text-align: center; margin-top: 3.5rem; padding-top: 1.5rem; border-top: 1px solid #E8E2D9; color: #7B8576; font-size: 0.9rem;">
        🌱 <strong>SoilMate</strong> — Built for Hacktoberfest 2026 DEV Challenge (Week 1: Touch Grass)<br>
        Open source under Apache-2.0 / MIT. Zero trackers. Free-tier cloud ready.
    </div>
    """,
    unsafe_allow_html=True,
)
