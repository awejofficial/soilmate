# SoilMate — Privacy & Data Sovereignty Policy

**Effective Date:** October 11, 2026  
**Commitment:** 100% Zero-Tracking, Local Sovereignty, and ₹0 Infrastructure Cost.

---

## 1. Principles of Privacy in SoilMate

Gardening is an intimate, grounding outdoor activity. SoilMate believes gardening tools should never surveil users or harvest personal data.

Our privacy architecture follows four core guarantees:

### 1. Zero Personal Tracking
- **No Analytics Trackers:** SoilMate does not include Google Analytics, Meta Pixel, Hotjar, or any third-party behavioral trackers.
- **No User Accounts:** You do not need to register, provide an email, or sign in with social media to generate plans or use the application.
- **No Coarse/Fine Geolocation:** SoilMate does not request browser GPS permissions or IP geocoding. Users manually type their general city or region (e.g., "Austin" or "Bangalore") to obtain regional planting recommendations.

### 2. Local-First Data Sovereignty
- **Session-Based Storage:** By default, your garden profile, 7-day checklist progress, and journal notes reside in your active browser session (`st.session_state`).
- **Portable JSON Backups:** You retain full custody of your records. You can download a structured backup (`soilmate_backup.json`) at any time under **⚙️ Settings & Backup** and restore it across devices or sessions.
- **One-Click Data Deletion:** Clicking "⚠️ Reset All Garden Data" immediately flushes your profile, active plans, and journal logs.

### 3. Hosted AI Inference Boundaries
- **Minimal Prompt Payloads:** When hosted AI mode is activated using `HF_TOKEN`, only high-level garden parameters (city name, sunlight tier, space footprint, goal) and candidate plant IDs from `data/plants.json` are passed to the inference endpoint.
- **No Journal Transmission:** Your private journal entries, observations, and photos (if any) are **never** transmitted to the AI provider.
- **Offline / Deterministic Fallback Option:** If you prefer that zero requests leave the application, simply run SoilMate without configuring an `HF_TOKEN`. The deterministic horticultural engine executes 100% locally with zero external network transmission.

### 4. Zero Monetization & Free-Tier Operation
SoilMate is completely open-source and free:
- Budget: ₹0.
- No ads, sponsorships, paywalls, or premium tiers.
- Hosted using public open-source free tiers (Streamlit Community Cloud and Hugging Face Serverless Inference Providers).

---

## 5. Contact & Auditing
SoilMate is open-source under the Apache-2.0 / MIT license. The entire codebase, including API interaction handlers and data serialization logic, is open for public inspection and auditing in this repository.
