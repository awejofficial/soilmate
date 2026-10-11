# SoilMate — Cloud Deployment Guide

**Deployment Target:** Streamlit Community Cloud + GitHub  
**Cost:** ₹0 (100% Free Tier)  
**No Local Dependencies:** Operates completely in the cloud with zero localhost or desktop requirements.

---

## 1. Overview

SoilMate is architected for zero-friction cloud deployment. Because home gardeners access the tool from smartphones and laptops across diverse environments, the system requires no local terminal commands, no Docker daemon, and no local LLM runtime (such as Ollama).

All inference is executed via hosted open-weight inference APIs or handled locally within Python using the verified deterministic horticultural fallback engine.

---

## 2. Prerequisites

1. A **GitHub account** with this repository pushed to `main`.
2. A free **Streamlit Community Cloud** account ([share.streamlit.io](https://share.streamlit.io)).
3. (Optional for AI enhancement) A free **Hugging Face** user access token ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)).

---

## 3. Step-by-Step Streamlit Community Cloud Deployment

### Step 1: Push Repository to GitHub
Ensure all code and dependencies are committed to your GitHub repository:
```bash
git add .
git commit -m "feat: complete SoilMate MVP with hybrid AI and 7-day checklist"
git push origin main
```

### Step 2: Create New App on Streamlit Cloud
1. Sign in to [share.streamlit.io](https://share.streamlit.io).
2. Click **"New app"**.
3. Select your repository: `username/soilmate`.
4. Set **Branch**: `main`.
5. Set **Main file path**: `app.py`.
6. Set **App URL**: `soilmate.streamlit.app` (or chosen custom subdomain).

### Step 3: Configure Secrets (Optional AI Tokens)
In your app's dashboard on Streamlit Community Cloud:
1. Click **App Settings** (three dots in lower right).
2. Navigate to **Secrets**.
3. Enter the configuration in TOML format:

```toml
APP_ENV = "production"
AI_PROVIDER = "huggingface"
AI_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
HF_TOKEN = "hf_your_free_user_access_token_here"
REQUEST_TIMEOUT_SECONDS = 30
```

> [!TIP]
> **Zero-Cost Guarantees:** If you choose not to provide `HF_TOKEN` (or if your monthly Hugging Face serverless credits expire), SoilMate automatically and seamlessly defaults to its **Deterministic Horticultural Engine**. No errors are thrown, and users experience zero disruption.

### Step 4: Deploy & Verify
1. Click **Deploy!**
2. Watch the Streamlit build logs. Streamlit will install packages from `requirements.txt`:
   - `streamlit>=1.38.0`
   - `requests>=2.31.0`
   - `pydantic>=2.6.0`
   - `python-dotenv>=1.0.1`
   - `pytest>=8.0.0`
3. Once deployed, test the following checklist:
   - [ ] Page loads with the custom earthy forest green theme.
   - [ ] Fill out the Garden Profile and click "Generate My 7-Day Outdoor Plan".
   - [ ] Verify recommended plants and 7-day tasks appear.
   - [ ] Switch to **"☀️ Outdoor Mode"** to verify high-contrast layout.
   - [ ] Toggle a task checkbox and verify progress updates.
   - [ ] Log an entry in the **"📖 Garden Journal"**.
   - [ ] Test the **"💾 Download Backup (JSON)"** in Settings.

---

## 4. Production Environment Variables Reference

| Variable | Required | Default Value | Description |
|---|---|---|---|
| `APP_ENV` | No | `production` | Active runtime environment indicator |
| `AI_PROVIDER` | No | `huggingface` | AI provider identifier |
| `AI_MODEL` | No | `meta-llama/Llama-3.2-3B-Instruct` | Open-weight model hosted on Hugging Face |
| `HF_TOKEN` | No | `None` | User access token for serverless inference |
| `REQUEST_TIMEOUT_SECONDS` | No | `30` | Network request timeout for inference calls |

---

## 5. Troubleshooting & FAQ

#### Q: What happens if Hugging Face returns HTTP 429 (Rate Limit) or 503 (Model Loading)?
**A:** `ai_service.py` intercepts all HTTP errors, timeouts, and JSON decode errors. It automatically invokes `recommendation_engine.generate_fallback_plan()`, which constructs a verified 7-day plan from `data/plants.json`. The user is informed via a clear status badge without seeing stack traces or error screens.

#### Q: Does SoilMate require a database?
**A:** No. SoilMate's MVP uses in-memory session persistence alongside portable JSON backup import/export. This guarantees ₹0 hosting costs and protects gardener privacy.
