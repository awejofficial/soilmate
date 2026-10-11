# SoilMate — Product Requirements Document (PRD)

**Version:** 1.0  
**Status:** MVP — Development  
**Project Type:** Open-source AI-powered gardening assistant  
**Challenge:** Hacktoberfest 2026 DEV Challenge — Week 1: Touch Grass  
**Target MVP Date:** October 11, 2026  
**Platform:** Responsive web application / Progressive Web App (PWA)

---

## 1. Product Overview

### 1.1 Product Name

**SoilMate — Grow More. Scroll Less.**

### 1.2 Product Vision

SoilMate is an open-source, AI-powered gardening assistant that helps beginners grow herbs, vegetables, and other suitable plants using personalized, practical, and region-aware gardening guidance.

The product aims to reduce the gap between learning about gardening and actually doing it.

Users describe their growing environment, receive a personalized garden plan, and follow a short list of outdoor activities without needing to remain connected to the application.

### 1.3 Problem Statement

Beginners often struggle to start gardening because they do not know which plants are appropriate for their location, available sunlight, space, or growing season.

Existing digital resources may provide generic recommendations, require constant internet access, or encourage prolonged screen interaction.

Users need a simple tool that converts their gardening goals into actionable steps, works reliably when AI services are unavailable, and encourages hands-on outdoor activity.

### 1.4 Proposed Solution

SoilMate combines curated gardening knowledge with open-weight AI to generate personalized gardening plans.

The application will provide:

- Garden profile creation.
- Region-aware plant recommendations.
- AI-generated gardening plans and care instructions.
- A seven-day gardening task checklist.
- Local task and journal persistence.
- Local AI inference with optional hosted inference.
- A rule-based fallback when AI is unavailable.
- An outdoor-first interface designed to minimize screen time.

### 1.5 Value Proposition

**SoilMate transforms gardening questions into practical outdoor actions using open AI technology, locally stored information, and accessible gardening guidance.**

---

## 2. Target Users

### Primary Persona: Beginner Gardener

- Has little or no gardening experience.
- Wants to grow vegetables or herbs at home.
- Has limited space, such as a balcony, terrace, or small backyard.
- Needs simple instructions rather than technical agricultural terminology.
- May have inconsistent internet access.

### Secondary Persona: Urban Home Gardener

- Already grows a few plants.
- Wants help planning planting schedules and care routines.
- Needs recommendations based on sunlight, available space, and local conditions.

### Tertiary Persona: Privacy-Conscious Open-Source User

- Prefers local processing when possible.
- Wants control over model selection and inference.
- Does not want personal garden information sent to a hosted AI service unnecessarily.

---

## 3. Product Goals and Non-Goals

### 3.1 Goals

1. Help a beginner create a usable garden plan in under two minutes, excluding unusually slow model inference.
2. Provide practical recommendations based on the user's garden profile and verified reference data.
3. Support local AI inference and optional hosted AI inference.
4. Keep previously saved plans and task lists accessible offline.
5. Provide a useful fallback when AI services fail.
6. Encourage users to complete real-world gardening activities.
7. Demonstrate why open-weight AI and open-source software are useful in a practical application.

### 3.2 Non-Goals for the MVP

The initial release will not include:

- User registration or social login.
- Community feeds or gardening forums.
- Payments or subscriptions.
- Plant disease diagnosis using images.
- Automated pesticide or fertilizer prescriptions.
- Advanced crop-yield prediction.
- Full agricultural management for commercial farms.
- Live weather forecasting.
- Complex geospatial mapping.
- Multi-user cloud synchronization.
- Guaranteed crop success or professional agronomic advice.

These features may be considered after the MVP is stable.

---

## 4. Core User Journey

1. The user opens SoilMate.
2. The user enters their location and garden details.
3. SoilMate checks the available gardening reference data.
4. The application generates recommendations using local AI, optional hosted AI, or deterministic fallback rules.
5. The user reviews suggested plants and the care plan.
6. SoilMate presents a seven-day checklist.
7. The user takes the checklist outside and completes gardening activities.
8. Completed tasks and journal notes are saved locally.
9. The user returns when needed to review progress or update their plan.

**Core principle:** The application should help users leave the screen and perform the recommended activity.

---

## 5. Functional Requirements

### FR-01: Garden Profile

**Priority:** P0 — Must have

Users must be able to provide:

- City or region.
- Garden type: balcony pots, terrace, or backyard.
- Sunlight availability.
- Available growing space.
- Gardening goal: vegetables, herbs, or beginner gardening.
- Optional soil type and growing-container details.

**Acceptance criteria:**

- Required fields are validated.
- The user can generate a plan without creating an account.
- The profile is available for subsequent plan generation.
- The interface explains when additional information is needed.

### FR-02: Plant Recommendation Engine

**Priority:** P0 — Must have

The application must maintain a curated plant reference dataset.

Each plant record should contain:

- Common name.
- Scientific name, where available.
- Suitable growing conditions.
- Sunlight requirements.
- Watering guidance.
- Space or container requirements.
- Suitable planting period or seasonal guidance.
- Source and verification information.

**Acceptance criteria:**

- Recommendations consider the user's garden type and sunlight.
- Unsupported seasonal assumptions are not presented as verified facts.
- Planting periods are sourced from appropriate regional references.
- The application can display reference-based recommendations without AI.

### FR-03: AI Garden Planner

**Priority:** P0 — Must have

The AI service generates a structured gardening plan based on the user profile and curated plant data.

The output should include:

- A short summary.
- Recommended plants with reasons.
- Preparation instructions.
- Basic care instructions.
- A seven-day task list.
- Relevant limitations or verification notes.

**Acceptance criteria:**

- The model receives relevant profile details and reference information.
- The application validates the response structure.
- Malformed model responses do not crash the application.
- The user can distinguish AI-generated explanations from verified reference data.
- The plan avoids unsupported guarantees.

### FR-04: Hybrid AI Provider

**Priority:** P0 — Must have

The application supports:

1. **Local inference:** an open-weight model running through a local runtime such as Ollama.
2. **Hosted inference:** an optional compatible inference provider serving an open-weight model.
3. **Rule-based fallback:** deterministic recommendations generated from curated data.

**Provider behavior:**

- Attempt the configured local model first when local-first mode is enabled.
- Use hosted inference only when configured and permitted by the selected settings.
- If inference fails, use the rule-based fallback.
- Clearly identify which mode generated the plan.

**Acceptance criteria:**

- The app works without an inference API key.
- Hosted inference is never silently substituted for local inference when the user has selected local-only mode.
- API keys remain server-side and are never committed to source control.
- Provider timeouts and invalid responses are handled safely.
- The application remains usable if both AI providers are unavailable.

### FR-05: Seven-Day Gardening Plan

**Priority:** P0 — Must have

The system presents a manageable schedule of gardening activities.

Examples include:

- Inspecting sunlight exposure.
- Checking container drainage.
- Preparing suitable growing containers.
- Reviewing locally verified planting guidance.
- Inspecting soil moisture.
- Recording plant growth.

Actual planting, watering, and care instructions must be appropriate for the selected plant and conditions.

**Acceptance criteria:**

- Tasks are presented in a readable checklist.
- Each task has a title and a short instruction.
- Tasks can be marked complete.
- Tasks do not require an active AI connection once saved.
- The interface encourages outdoor completion.

### FR-06: Local Persistence

**Priority:** P0 — Must have

The application stores the user's garden profile, saved plan, task completion status, and journal notes locally.

**Acceptance criteria:**

- Saved data remains available after a page refresh or application restart, subject to the selected storage implementation.
- The app can display the last saved plan offline.
- Users can update or reset their local data.
- The application does not require an account for basic functionality.

**Implementation note:** Use browser storage for a browser-based implementation or local JSON/SQLite for a suitable local application architecture. Do not claim browser-local data is encrypted or backed up unless that functionality is implemented.

### FR-07: Garden Journal

**Priority:** P1 — Should have

Users can add short notes about completed gardening activities.

Journal entries may include:

- Date.
- Task completed.
- Observations.
- Plant growth notes.
- Optional photographs, if supported.

**Acceptance criteria:**

- Entries can be created and viewed.
- Entries are associated with the correct garden or task.
- Notes remain available offline when stored locally.
- Users can delete entries.

For a deadline-focused MVP, a text-only journal is sufficient.

### FR-08: Outdoor Mode

**Priority:** P0 — Must have

Outdoor Mode provides a distraction-free view of the next gardening tasks.

It should include:

- Today's tasks.
- Large, easy-to-use completion controls.
- Minimal navigation.
- Short instructions.
- A reminder to put the phone away after reviewing the task.

**Acceptance criteria:**

- Tasks are readable on a mobile screen.
- Completing a task updates saved progress.
- The interface does not require continuous conversation with AI.
- Previously saved tasks remain usable without internet access.

### FR-09: Offline Support

**Priority:** P0 — Must have

The application should distinguish between offline access to saved content and offline AI inference.

**Acceptance criteria:**

- Previously saved plans can be viewed offline.
- Saved tasks can be completed offline.
- The curated fallback engine can operate without hosted services.
- Local inference works offline when the model and required application resources are already installed.
- Hosted inference is unavailable without connectivity and reports this limitation clearly.

A PWA service worker and installable application experience may be added if time permits; they are not prerequisites for the initial working MVP.

---

## 6. Non-Functional Requirements

### NFR-01: Performance

- The application should load without unnecessary dependencies.
- Form submission should show an immediate loading state.
- AI requests must have configurable timeouts.
- Saved tasks should update without requiring a model request.
- A deterministic fallback should return promptly.

### NFR-02: Usability

- Mobile-first responsive layout.
- Plain-language instructions.
- Accessible labels and keyboard navigation.
- Clear loading, success, empty, and error states.
- Minimal visual distractions.

### NFR-03: Reliability

- External AI failures must not crash the application.
- Invalid output must be rejected or safely handled.
- A plan must remain available after it has been saved.
- Model output must be validated before display.

### NFR-04: Privacy

- No account is required for the MVP.
- Garden profiles and journal entries remain local by default.
- Hosted inference must be optional and disclosed.
- Only necessary profile information should be sent to hosted inference.
- Secrets must be stored in environment variables or a secrets manager.
- Local persistence limitations must be documented.

### NFR-05: Maintainability

- AI provider logic must be separate from the UI.
- Plant reference data must be separate from AI-generated text.
- Provider integrations should be replaceable.
- Configuration and installation instructions must be documented.
- The codebase should use clear modules and meaningful error handling.

### NFR-06: Accessibility

- Text must be readable on small screens.
- Controls must have descriptive labels.
- Status must not be communicated by color alone.
- The checklist must support keyboard interaction.

---

## 7. Recommended Technical Architecture

### Frontend

**Streamlit** for the initial Python MVP.

Responsibilities:

- Garden profile form.
- Plan display.
- Outdoor checklist.
- Journal interface.
- Provider status and error messages.

### Application Logic

**Python**

Responsibilities:

- Profile validation.
- Plant dataset filtering.
- Plan construction.
- Output validation.
- Task and journal management.

### AI Layer

- **Local inference:** Ollama with a suitable open-weight instruct model, such as Qwen2.5 3B Instruct, subject to hardware testing.
- **Hosted inference:** An optional provider compatible with an appropriate open-weight model.
- **Fallback:** A deterministic recommendation engine based on curated plant records.

### Data Layer

For the MVP:

- `plants.json` for curated reference data.
- Local storage for the garden profile, saved plans, tasks, and journal.

A database is unnecessary unless the chosen application architecture requires it.

### Suggested Project Structure

```text
soilmate/
├── app.py
├── garden_data.py
├── ai_service.py
├── recommendation_engine.py
├── storage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── data/
│   └── plants.json
├── tests/
│   ├── test_recommendations.py
│   ├── test_ai_service.py
│   └── test_storage.py
└── docs/
    ├── PRD.md
    ├── DEPLOYMENT_PRD.md
    └── architecture.md
```

---

## 8. Data and Recommendation Strategy

The application should use a small, verified dataset rather than relying exclusively on an LLM's general knowledge.

Each plant record should identify:

- The plant and variety, where relevant.
- Recommended conditions.
- Seasonal limitations.
- Geographic relevance.
- Reference source.
- Last verification date.

For an initial Maharashtra-focused demonstration, candidate crops can be researched using relevant state agricultural university or horticultural extension resources.

Do not hardcode a generic planting calendar as universally correct. Local climate, rainfall, season, soil, variety, and container conditions can affect suitability.

The AI service should receive relevant reference records and use them to explain recommendations. It should not invent missing reference data.

---

## 9. User Interface Requirements

### Screen 1: Home

Purpose: Explain the product and help users begin.

Elements:

- SoilMate branding.
- Short value proposition.
- Create or update garden profile.
- Continue with saved plan, if one exists.

### Screen 2: Garden Profile

Purpose: Collect relevant growing conditions.

Elements:

- Location field.
- Garden type selector.
- Sunlight selector.
- Available space selector.
- Gardening goal.
- Generate plan button.

### Screen 3: Garden Plan

Purpose: Present actionable recommendations.

Elements:

- Summary of the garden conditions.
- Recommended plants.
- Reasons for recommendations.
- Basic care guidance.
- Seven-day task schedule.
- AI provider or fallback indicator.

### Screen 4: Outdoor Mode

Purpose: Make tasks usable away from the screen.

Elements:

- Today's tasks.
- Task completion controls.
- Short care instructions.
- Return-to-journal action.
- Minimal interface chrome.

### Screen 5: Garden Journal

Purpose: Record observations and progress.

Elements:

- Completed tasks.
- Dated notes.
- Add note action.
- Edit or delete actions.

**Design direction:** Natural, clean, and functional. Use an earthy green accent, warm off-white background, dark readable text, restrained borders, and generous spacing. Avoid excessive gradients, glassmorphism, heavy shadows, or dashboard clutter.

---

## 10. Success Metrics

These are initial product targets, not measured results.

| Metric | Initial target |
|---|---|
| Garden profile completion | At least 90% of users who start the form |
| Plan generation | Successful output or usable fallback in at least 95% of test scenarios |
| Saved task persistence | 100% of defined persistence tests pass |
| Offline saved-plan access | Works in all defined offline acceptance tests |
| AI output validation | All displayed plans pass schema validation |
| Core mobile usability | All core actions work at the target mobile viewport |
| Outdoor usefulness | At least one documented real-world task test |
| Installation reproducibility | A new developer can follow the README successfully |

Do not report user engagement, crop success, or offline performance as proven without actual testing.

---

## 11. MVP Testing Plan

### Functional Tests

- Submit a valid garden profile.
- Reject missing required information.
- Generate a plan from reference data.
- Parse valid AI output.
- Reject malformed JSON and unexpected output types.
- Handle model timeouts.
- Verify fallback recommendations.
- Mark tasks complete and refresh the app.
- Save and retrieve journal entries.

### Offline Tests

- Disable the internet connection.
- Open the previously saved plan.
- Complete a saved task.
- Verify that the app does not attempt hosted inference without connectivity.
- Confirm that local inference is available only if the local runtime and model are installed.

### Security Tests

- Search the repository for accidentally committed API keys.
- Verify that hosted credentials are not included in user-visible output.
- Ensure profile details are not sent to hosted inference in local-only mode.
- Confirm that model output is treated as untrusted data.

### Gardening Quality Tests

- Check each candidate plant against the selected regional reference source.
- Review sunlight and space constraints.
- Verify that seasonal guidance is appropriately qualified.
- Confirm that unsupported disease, fertilizer, or pesticide advice is not presented as established fact.

---

## 12. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Local model is too slow on limited RAM | Make local inference optional and retain a fallback |
| Hosted provider is unavailable | Use local inference or deterministic recommendations |
| AI produces incorrect gardening advice | Ground recommendations in verified reference data and validate output |
| User loses local data | Document storage limitations and provide data export if time permits |
| Scope expands beyond the deadline | Prioritize the P0 feature set |
| Open-weight model licensing is misunderstood | Document the exact model and license used |
| Offline claims are overstated | Test and document precisely which functions work offline |

---

## 13. Development Plan

### Phase 1: Working Core

- Create the application.
- Build the garden profile.
- Create the initial curated plant dataset.
- Implement the deterministic recommendation engine.
- Display a basic garden plan.

### Phase 2: AI Integration

- Integrate local Ollama inference.
- Add an optional hosted provider.
- Validate model output.
- Add timeouts and fallback behavior.
- Display the selected generation mode.

### Phase 3: Outdoor Experience

- Add the seven-day checklist.
- Persist task completion.
- Add the text-based garden journal.
- Improve mobile layout and offline access.

### Phase 4: Release

- Test the complete user journey.
- Prepare README and setup instructions.
- Add screenshots and an architecture diagram.
- Publish the GitHub repository.
- Document genuine test results.
- Publish the DEV challenge article.

If time runs short, finish Phases 1 and 3 with a reliable fallback before polishing hosted AI integration.

---

## 14. Hacktoberfest Submission Requirements

The project should demonstrate that open-source AI is central to its implementation.

The repository should include:

- Clear project overview.
- Installation and execution instructions.
- Exact model name and license.
- Local and hosted inference configuration.
- Offline behavior and limitations.
- Verified data sources.
- Architecture documentation.
- Screenshots or a demonstration.
- Tests and known limitations.
- An open-source software license for the project itself.

The DEV article should explain:

1. The problem SoilMate addresses.
2. How the application works.
3. Why local and hosted open-weight inference are both supported.
4. How privacy and offline availability are handled.
5. What was tested outdoors.
6. What remains incomplete and what will be improved next.

The project should be represented honestly: planned features must not be described as implemented, and screenshots must reflect the real application.

---

## 15. Definition of Done

The MVP is considered complete when:

- A user can enter a garden profile.
- The application produces a useful plan from verified data.
- Local AI inference can be enabled and tested.
- Hosted inference is optional and correctly configured.
- Failure of both AI providers does not break the application.
- The user can view and complete saved gardening tasks offline.
- The core experience works on a mobile viewport.
- The README explains installation, model configuration, data sources, and limitations.
- The repository is publicly accessible.
- The DEV submission accurately describes the implemented product.

---

## 16. Future Roadmap

After the MVP, potential improvements include:

- Weather-aware recommendations using a reliable weather source.
- More regional plant datasets.
- Image-based plant identification using an appropriate vision model.
- Optional plant-growth photo journal.
- Installable PWA support.
- Exportable garden plans.
- Multiple gardens per user.
- Improved localization and language support.
- More robust horticultural source citations.

These features should be added only when they improve gardening outcomes without making the product unnecessarily screen-intensive.

---

## Final Product Principle

**SoilMate is not intended to replace gardeners' judgment or trusted horticultural knowledge. It is designed to help beginners take their first practical steps toward growing plants.**

Open-source AI supplies adaptable assistance; verified reference data supplies grounding; local persistence supplies continuity; and Outdoor Mode connects the digital plan to real-world action.

The measure of success is not how long users spend in SoilMate. It is whether the application helps them get outside and grow something.
