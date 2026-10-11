# SoilMate — Implementation Traceability Matrix

**Version:** 1.0  
**Verification Date:** October 11, 2026  
**Status:** 100% Implemented & Verified  

---

## 1. Traceability Summary

This matrix maps every functional requirement (FR-01 through FR-08) from `PRD.md` and deployment requirement (DEP-01 through DEP-08) from `DEPLOYMENT_PRD.md` to its implementation files, functions, and automated test cases.

---

## 2. Functional Requirements Traceability Matrix

| Req ID | Requirement Description | Implementation Location | Verification / Test Case | Status |
|---|---|---|---|---|
| **FR-01** | **Garden Profile Intake**<br>Location, garden type, sunlight, space footprint, goals, container details. | `garden_data.py::GardenProfile`<br>`app.py` Form `garden_profile_form`<br>`storage.py::set_profile()` | `tests/test_storage.py::test_profile_and_plan_storage` | ✅ PASS |
| **FR-02** | **Plant Recommendation Engine & Verified Catalog**<br>15 curated plants, botanical metadata, sunlight hours, depth, watering, RHS citations. | `data/plants.json`<br>`garden_data.py::load_plants()`<br>`recommendation_engine.py::score_plant()` | `tests/test_plants_data.py::test_plants_json_schema_validation`<br>`tests/test_plants_data.py::test_filter_plants` | ✅ PASS |
| **FR-03** | **AI Garden Planner**<br>Generates structured summary, plant reasons, prep steps, care steps, 7-day tasks, grounded prompt. | `ai_service.py::_build_ai_prompt()`<br>`ai_service.py::_clean_json_response()`<br>`ai_service.py::generate_garden_plan()` | `tests/test_ai_service.py::test_clean_json_response_markdown_blocks`<br>`tests/test_ai_service.py::test_generate_garden_plan_successful_ai_parse` | ✅ PASS |
| **FR-04** | **Hybrid AI Provider & Fallback**<br>Hosted inference with open-weight models, automatic fallback on timeout/rate limit, no committed keys. | `ai_service.py::get_provider_status()`<br>`ai_service.py::generate_garden_plan()`<br>`recommendation_engine.py::generate_fallback_plan()` | `tests/test_ai_service.py::test_generate_garden_plan_fallback_when_no_token`<br>`tests/test_ai_service.py::test_generate_garden_plan_fallback_on_api_error` | ✅ PASS |
| **FR-05** | **Seven-Day Gardening Plan**<br>7 outdoor tasks (sunlight audit, drainage, soil, sowing, watering, moisture check, review), checklist UI. | `garden_data.py::TaskItem`<br>`recommendation_engine.py::generate_fallback_plan()`<br>`app.py` View `7-Day Outdoor Plan` | `tests/test_recommendation_engine.py::test_generate_fallback_plan_completeness`<br>`tests/test_storage.py::test_toggle_task_completion` | ✅ PASS |
| **FR-06** | **Local Persistence & Data Portability**<br>Session state retention, portable JSON export/import, zero login requirement. | `storage.py::init_session_state()`<br>`storage.py::export_state_to_json()`<br>`storage.py::import_state_from_json()` | `tests/test_storage.py::test_export_and_import_backup_roundtrip`<br>`tests/test_storage.py::test_init_session_state` | ✅ PASS |
| **FR-07** | **Garden Journal**<br>Observation logging, date, task tag, plant tag, growth stage, entry deletion. | `garden_data.py::JournalEntry`<br>`storage.py::add_journal_entry()`<br>`storage.py::delete_journal_entry()`<br>`app.py` View `Garden Journal` | `tests/test_storage.py::test_journal_operations` | ✅ PASS |
| **FR-08** | **Outdoor Mode**<br>High-contrast, distraction-free view, today's immediate task, large touch targets, touch-grass prompt. | `app.py` View `Outdoor Mode`<br>CSS classes `.outdoor-hero-card`, `.outdoor-touch-grass-box` | Verified in UI review & component test fixtures | ✅ PASS |

---

## 3. Deployment Requirements Traceability Matrix

| Req ID | Requirement Description | Implementation Location | Verification Evidence | Status |
|---|---|---|---|---|
| **DEP-01** | **Public Availability**<br>Public HTTPS deployment via Streamlit Community Cloud; no localhost dependencies. | `docs/DEPLOYMENT.md`<br>`app.py` | Cloud deployment workflow documented and verified | ✅ PASS |
| **DEP-02** | **Cloud-Only AI**<br>Hosted serverless inference; zero local Ollama or desktop runtime processes. | `ai_service.py` (Hugging Face router endpoints) | Automated mock tests; no local daemons in codebase | ✅ PASS |
| **DEP-03** | **Free-Tier Limits Handling**<br>Handles HTTP 429, 503, and monthly quota limits gracefully. | `ai_service.py` (error try/except block) | `tests/test_ai_service.py::test_generate_garden_plan_fallback_on_api_error` | ✅ PASS |
| **DEP-04** | **AI Fallback**<br>Deterministic planting plan grounded in verified reference data. | `recommendation_engine.py::generate_fallback_plan()` | `tests/test_recommendation_engine.py::test_generate_fallback_plan_completeness` | ✅ PASS |
| **DEP-05** | **Cloud Persistence & Portability**<br>Portable JSON backup import/export, zero server filesystem dependence. | `storage.py::export_state_to_json()`<br>`storage.py::import_state_from_json()` | `tests/test_storage.py::test_export_and_import_backup_roundtrip` | ✅ PASS |
| **DEP-06** | **Security & Privacy**<br>Credentials in secrets, `.env.example`, no committed keys, zero tracking cookies. | `.env.example`<br>`.gitignore`<br>`docs/PRIVACY.md` | Audit confirmed clean repository with zero committed secrets | ✅ PASS |
| **DEP-07** | **Reliability & Usability**<br>Loading indicators, timeouts (25-30s), mobile-responsive natural design. | `app.py` (st.spinner, responsive columns, organic earthy CSS) | Responsive styling inspected and verified | ✅ PASS |
| **DEP-08** | **Deployment & CI**<br>GitHub repository, pinned dependencies, automated tests on GitHub Actions. | `requirements.txt`<br>`.github/workflows/ci.yml` | GitHub Actions workflow configuration verified | ✅ PASS |
