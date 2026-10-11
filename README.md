# 🌱 SoilMate — Grow More. Scroll Less.

[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest%202026-Week%201%3A%20Touch%20Grass-2D5A27.svg)](https://dev.to)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Hosted AI](https://img.shields.io/badge/AI-Open--Weight%20Inference-green.svg)](https://huggingface.co/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Zero-Cost Budget](https://img.shields.io/badge/Hosting%20Cost-%E2%82%B90%20%2F%20Free%20Tier-success.svg)](https://share.streamlit.io)

> **SoilMate** is an open-source, mobile-responsive gardening assistant built for the **Hacktoberfest 2026 DEV Open-Source AI Challenge (Week 1: "Touch Grass")**. It transforms gardening goals into actionable 7-day outdoor activities, minimizes screen time, and works reliably with zero local dependencies or paid infrastructure.

---

## 🌟 The Philosophy: "Grow More. Scroll Less."

Most gardening applications trap beginners in social feeds, forums, and endless screens. **SoilMate does the exact opposite:**

1. **Ask Once:** Enter your city, sunlight exposure, and space footprint.
2. **Receive Actionable Plan:** Get a grounded 7-day schedule with verified plant recommendations.
3. **Step Outside & Touch Grass:** Switch to **Outdoor Mode**—a high-contrast, distraction-free view with one focused physical action per day (inspecting sunlight, testing pot drainage, smelling soil, sowing seeds).
4. **Put Phone Away:** SoilMate reminds you to leave your screen inside and enjoy the sun.

---

## ✨ Key Features

- **🛡️ Hybrid AI with Deterministic Fallback:** Uses hosted open-weight inference (e.g., Llama 3.2 / Qwen on Hugging Face Inference Providers) grounded in curated reference data. If the AI is unconfigured, rate-limited, or offline, SoilMate automatically activates its deterministic horticultural engine with zero errors.
- **🌿 Curated Botanical Reference Catalog:** 15 verified plant varieties (herbs, vegetables, companion flowers) complete with sunlight hours, container depths, watering advice, and Royal Horticultural Society (RHS) citations.
- **☀️ Distraction-Free Outdoor Mode:** Designed specifically for mobile outdoor use in direct sunlight with high-contrast text, extra-large touch targets, and a single daily action.
- **📋 7-Day Outdoor Checklist:** Step-by-step physical gardening schedule with estimated durations, completion tracking, and sensory touch-grass tips.
- **📖 Private Garden Journal:** Log soil moisture observations, sprout dates, and growth stages with zero cloud tracking.
- **💾 Portable JSON Backups:** Export and restore your complete garden profile, checklist progress, and journal notes with 100% data sovereignty.
- **☁️ ₹0 Cloud Deployment:** Runs 100% online on Streamlit Community Cloud without local daemons, Ollama, or paid cloud databases.

---

## 🏗️ System Architecture

```
                    +---------------------------------------+
                    |       SoilMate Streamlit Web App      |
                    +---------------------------------------+
                                        |
       +--------------------------------+--------------------------------+
       |                                                                 |
       v                                                                 v
+-------------------------------+                     +-------------------------------+
|     Hosted AI Provider        |                     |   Deterministic Fallback      |
|  (Hugging Face Serverless)    |                     |   (recommendation_engine.py)  |
|  Open-Weight Model Inference  |                     |   Rule-Based Scoring Engine   |
+-------------------------------+                     +-------------------------------+
       |                                                                 |
       +--------------------------------+--------------------------------+
                                        |
                                        v
                       +----------------------------------+
                       |    Verified Botanical Catalog    |
                       |        (data/plants.json)        |
                       +----------------------------------+
                                        |
                                        v
                       +----------------------------------+
                       |     Portable Session Storage     |
                       |           (storage.py)           |
                       +----------------------------------+
```

For complete architectural specifications, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🚀 Quickstart (Local Development)

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/your-username/soilmate.git
cd soilmate

# Create virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run SoilMate Locally

```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

### 4. (Optional) Configure Hosted AI

Copy `.env.example` to `.env` and supply your free Hugging Face User Access Token:

```env
HF_TOKEN=hf_your_free_huggingface_token
AI_MODEL=meta-llama/Llama-3.2-3B-Instruct
REQUEST_TIMEOUT_SECONDS=30
```

> **Note:** If `HF_TOKEN` is left blank, SoilMate runs seamlessly in 100% deterministic offline-ready fallback mode at ₹0 cost.

---

## 🧪 Automated Testing & CI

SoilMate includes a comprehensive Pytest test suite covering data validation, recommendation scoring, AI fail-safe triggers, and storage roundtrips:

```bash
# Run test suite
pytest -v

# Run with concise tracebacks
pytest -v --tb=short
```

Automated testing runs on GitHub Actions across Python 3.11 and 3.12 (`.github/workflows/ci.yml`).
For detailed test coverage documentation, see [docs/TESTING.md](docs/TESTING.md).

---

## 🌐 Deploy to Streamlit Community Cloud (₹0 Budget)

1. Push your code to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Connect your repository, set **Main file path** to `app.py`, and click **Deploy**.
4. In App Settings > **Secrets**, optionally add `HF_TOKEN`.

Detailed deployment instructions and troubleshooting can be found in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## 📁 Repository Structure

```
soilmate/
├── .github/workflows/ci.yml     # Automated CI pipeline
├── data/
│   └── plants.json              # Curated 15-plant botanical reference dataset
├── docs/
│   ├── ARCHITECTURE.md          # Architectural diagrams & design documentation
│   ├── DEPLOYMENT.md            # Zero-cost cloud deployment guide
│   ├── DEV_SUBMISSION.md        # Official Hacktoberfest DEV Challenge submission
│   ├── IMPLEMENTATION_TRACEABILITY.md # Traceability matrix (PRD requirements)
│   ├── PRIVACY.md               # Privacy policy & data sovereignty guarantees
│   └── TESTING.md               # Test strategy and test case inventory
├── tests/
│   ├── test_ai_service.py       # AI client, prompt grounding, & fallback tests
│   ├── test_plants_data.py      # Dataset schema and botanical filter tests
│   ├── test_recommendation_engine.py # Scoring and 7-day plan generator tests
│   └── test_storage.py          # Session state, task toggles, & backup tests
├── .env.example                 # Environment configuration template
├── .gitignore                   # Safe git ignore rules
├── ai_service.py                # Hosted AI client with automatic fallback
├── app.py                       # Streamlit web application & Earthy UI
├── garden_data.py               # Pydantic v2 data schemas & data loader
├── recommendation_engine.py     # Deterministic rule-based horticultural engine
├── requirements.txt             # Pinned production dependencies
├── storage.py                   # Session state, task tracking, & JSON backup
└── README.md                    # Project documentation
```

---

## 🔒 Privacy & Data Sovereignty

- **Zero Trackers:** No Google Analytics, cookies, or telemetry.
- **Local Sovereignty:** Garden plans and journal logs reside in the browser session.
- **Portability:** Full JSON export and restore at any time.
- Read our full [docs/PRIVACY.md](docs/PRIVACY.md).

---

## 📜 License

Distributed under the Apache License 2.0. See `LICENSE` for details.
Built with 🌿 for Hacktoberfest 2026.
