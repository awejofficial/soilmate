# SoilMate — Testing Strategy & Verification Guide

**Version:** 1.0  
**Test Framework:** Pytest 8.0+  
**CI Engine:** GitHub Actions (`.github/workflows/ci.yml`)  

---

## 1. Testing Philosophy

SoilMate is designed to guide real beginners in outdoors gardening. Faulty assumptions, incorrect seasonal advice, broken checklists, or crashes when offline degrade the user's real-world gardening experience.

Our testing strategy enforces four pillars:
1. **Botanical Reference Integrity:** Every plant in `data/plants.json` must strictly satisfy the Pydantic schema with non-null sunlight hours, container depths, and outdoor actions.
2. **Deterministic Algorithmic Fallback:** The recommendation engine must produce complete, valid 7-day plans without network or AI availability.
3. **Graceful Degradation:** The AI service must intercept network failures, timeouts, rate limits, and malformed JSON, seamlessly triggering the fallback without surfacing errors to the user.
4. **State Persistence & Data Portability:** Task completions, timestamps, journals, and backup import/export cycles must preserve data fidelity without data loss.

---

## 2. Test Suite Breakdown

### 2.1 Botanical Reference Tests (`tests/test_plants_data.py`)
- `test_plants_json_file_exists`: Validates file presence and non-zero size.
- `test_plants_json_schema_validation`: Validates each plant profile against `Plant` Pydantic model:
  - Unique ID constraint.
  - Sunlight requirements (1-12 hours).
  - Minimum container depth (>= 4 inches).
  - Minimum container volume (>= 1 liter).
  - Non-empty touch grass activity and authoritative verification citation.
- `test_get_plant_by_id`: Verifies exact matching by ID and safe handling of missing IDs.
- `test_filter_plants`: Verifies multi-parameter catalog filtering (category, sunlight, difficulty).

### 2.2 Recommendation Engine Tests (`tests/test_recommendation_engine.py`)
- `test_score_plant_balcony_herb_matching`: Verifies that a compact herb with partial sun tolerance scores higher for an urban balcony than a large, sun-demanding crop.
- `test_select_recommended_plants`: Verifies top candidates are ranked with normalized scores (0-100) and categorized appropriately.
- `test_generate_fallback_plan_completeness`: Verifies fallback plan contains:
  - Exactly 7 daily tasks, numbered Day 1 through Day 7.
  - Instructions and touch grass sensory tips on every task.
  - Recommended plant candidates with specific reasoning.
  - Preparation steps, care instructions, and verification notes.
- `test_generate_fallback_plan_backyard`: Verifies backyard in-ground profile selects appropriate vegetable varieties.

### 2.3 AI Service & Fallback Tests (`tests/test_ai_service.py`)
- `test_provider_status_no_token`: Verifies status reports offline rule-based mode when no `HF_TOKEN` is found.
- `test_provider_status_with_token`: Verifies status identifies hosted AI mode when token is provided.
- `test_clean_json_response_markdown_blocks`: Tests sanitization of LLM responses wrapped in ` ```json ... ``` ` code fences.
- `test_clean_json_response_raw_braces`: Tests extraction of JSON with conversational preambles and postscripts.
- `test_build_ai_prompt_contains_grounded_candidates`: Verifies that candidates from the verified catalog are directly embedded in the system prompt.
- `test_generate_garden_plan_fallback_when_no_token`: Confirms deterministic fallback triggers immediately without errors when no token is configured.
- `test_generate_garden_plan_fallback_on_api_error`: Simulates HTTP 500 error and confirms smooth fallback to verified plan.
- `test_generate_garden_plan_successful_ai_parse`: Simulates HTTP 200 with structured JSON and verifies correct conversion into `GardenPlan` with `source="ai"`.

### 2.4 Persistence & Storage Tests (`tests/test_storage.py`)
- `test_init_session_state`: Verifies default session keys are created.
- `test_profile_and_plan_storage`: Verifies reading and writing `GardenProfile` and `GardenPlan`.
- `test_toggle_task_completion`: Verifies marking daily tasks completed, timestamp recording, and progress counting.
- `test_journal_operations`: Verifies adding observations, chronological sorting, and deleting entries.
- `test_export_and_import_backup_roundtrip`: Verifies complete JSON serialization, data clearing, and loss-free restoration.

---

## 3. Running the Test Suite Locally

Run the complete test suite using pytest:

```bash
# Run all tests with standard output
pytest -v

# Run with concise traceback on failure
pytest -v --tb=short

# Run specific module
pytest tests/test_recommendation_engine.py -v
```

---

## 4. Continuous Integration Pipeline

SoilMate runs continuous integration on GitHub Actions for every pull request and push to `main`:
- Matrix testing across Python 3.11 and Python 3.12.
- Direct JSON dataset integrity assertion before running tests.
- Full pytest execution with strict error exit codes.
