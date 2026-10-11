---
title: "SoilMate — Grow More. Scroll Less: An Open-Source AI Gardening Assistant for Week 1 (Touch Grass)"
published: true
tags: hacktoberfest, opensource, ai, python, touchgrass
cover_image: https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200&auto=format&fit=crop&q=80
canonical_url: https://github.com/awejofficial/soilmate
---

## 🌿 The Inspiration: What Happened to Touching Grass?

Gardening is supposed to be the ultimate antidote to digital burnout. It's about feeling cool, moist potting mix between your fingers, inhaling the fresh fragrance of crushed mint, and watching a humble seed sprout after days of patient waiting under the morning sun.

Yet, as beginners, whenever we set out to plant a few herbs on our balcony or terrace, what actually happens?

1. We search *"how to grow basil on a balcony"*.
2. We get sucked into 45-minute YouTube rabbit holes.
3. We browse Reddit gardening arguments about fertilizer ratios.
4. An hour later, our battery is down 20%, our screen time is up, and our pots are still empty.

For **Hacktoberfest 2026 DEV Open-Source AI Challenge (Week 1: "Touch Grass")**, we built **SoilMate** with one unapologetic product principle:

> **"Grow More. Scroll Less."**  
> Convert gardening ambitions into a 7-day schedule of hands-on physical outdoor activities, minimize screen time, and get you outside touching soil.

---

## 🚀 Introducing SoilMate

**SoilMate** is an open-source, mobile-responsive gardening companion powered by open-weight AI and verified botanical reference data.

Unlike generic chatbots that produce ungrounded hallucinations, SoilMate grounds every plan in a verified horticultural database of 15 home garden varieties cross-referenced with Royal Horticultural Society (RHS) and university agricultural extension manuals.

### 🌟 What Makes SoilMate Different?

1. **☀️ Distraction-Free "Outdoor Mode"**  
   Most apps are useless outdoors in bright sunlight with tiny buttons and endless feeds. SoilMate features an ultra-clean **Outdoor Mode**: high contrast, large touch targets, and a single card showing today's outdoor task. Above all, it has a friendly reminder: *"Step into the sun. Put your phone down and touch grass."*

2. **📋 The 7-Day Outdoor Action Plan**  
   Instead of overwhelming beginners with months of agricultural theory, SoilMate provides seven bite-sized daily outdoor tasks:
   - **Day 1:** Outdoor sunlight & microclimate audit (measuring where the direct light falls).
   - **Day 2:** Container sizing & drainage hole inspection.
   - **Day 3:** Aerating potting soil and pre-moistening the mix.
   - **Day 4:** Sowing seeds or transplanting with proper spacing.
   - **Day 5:** Gentle bottom watering and setting up mulch.
   - **Day 6:** Checking seedling moisture with a bare finger.
   - **Day 7:** First garden review, logging observations, and weekly care cadence.

3. **🛡️ Hybrid AI Architecture with Guaranteed Fallback (Budget ₹0)**  
   SoilMate connects to hosted open-weight models (like Llama 3.2 on Hugging Face Serverless Inference Providers). But what if you're offline, rate-limited, or don't have an API key?  
   **SoilMate never crashes.** Its built-in deterministic horticultural engine scores plants mathematically based on your sunlight, space, and goals, generating a verified 7-day plan at ₹0 cost.

4. **🔒 100% Data Sovereignty & Zero Trackers**  
   No user accounts, no login walls, no analytics trackers. All plans and journal entries live in your browser session with one-click JSON backup export/import.

---

## 🛠️ How We Built It

SoilMate is built with:
- **Streamlit (Python 3.11/3.12):** Reactive, high-performance web frontend styled with an organic earthy palette (forest green `#2D5A27`, terracotta `#C86D51`, and warm sand `#FAF8F5`).
- **Pydantic v2:** Strict schema validation for botanical profiles, garden inputs, checklists, and journal records.
- **Hugging Face Inference Providers:** Hosted open-weight LLMs serving grounded JSON responses.
- **Deterministic Horticultural Matcher:** Algorithmic ranking engine that factors in sunlight requirements, container volume, space footprint, and difficulty levels.
- **Pytest & GitHub Actions:** Comprehensive automated test suite ensuring dataset integrity, prompt sanitization, and fallback triggers.

### The Grounded Prompting Strategy

To eliminate AI hallucinations, we feed our verified candidate plants directly into the prompt:

```python
# ai_service.py snippet
def _build_ai_prompt(profile: GardenProfile, candidate_recommendations: List[PlantRecommendation]) -> str:
    candidates_data = [
        {
            "id": rec.plant.id,
            "name": rec.plant.common_name,
            "sunlight_hours_min": rec.plant.min_sunlight_hours,
            "container_depth_inches": rec.plant.min_container_depth_inches,
            "watering_guidance": rec.plant.watering_guidance,
            "outdoor_touch_grass_tip": rec.plant.touch_grass_activity,
        }
        for rec in candidate_recommendations
    ]

    return f"""You are SoilMate, an encouraging horticultural assistant.
User Profile: {profile.city_or_region}, {profile.garden_type}, {profile.sunlight}.
Verified Plant Candidates: {json.dumps(candidates_data)}

INSTRUCTIONS:
1. Ground your recommendations strictly on the provided verified candidates.
2. Output a structured 7-day outdoor action plan designed to get the user outdoors.
3. Return ONLY valid JSON matching the schema."""
```

If the API call fails or times out, SoilMate seamlessly triggers `generate_fallback_plan()`:

```python
# recommendation_engine.py snippet
def generate_fallback_plan(profile: GardenProfile) -> GardenPlan:
    top_picks = select_recommended_plants(profile, top_n=3)
    # Builds complete 7-day plan with verified RHS horticultural rules
    return GardenPlan(
        source="deterministic_fallback",
        provider_label="Deterministic Horticultural Engine (Verified Reference Fallback)",
        ...
    )
```

---

## 📸 Screenshots & Walkthrough

### 1. The Garden Intake & AI Plan
Visitors enter their city, space (balcony, terrace, backyard), sunlight hours, and experience level. Within seconds, SoilMate serves a grounded plan complete with plant cards, watering rules, and container depths.

### 2. Distraction-Free Outdoor Mode
When you head out to your balcony or backyard, launch Outdoor Mode. It strips away menus and displays today's task with large touch targets and a sensory touch-grass tip.

### 3. The 7-Day Checklist & Garden Journal
Check off each day as you complete it, track your percentage progress, and log daily observations like soil dampness or first sprouts.

---

## 🔗 Repository & Live Deployment

- **GitHub Repository:** [https://github.com/awejofficial/soilmate](https://github.com/awejofficial/soilmate)
- **Live Demo App:** [https://soilmate.streamlit.app](https://soilmate.streamlit.app)
- **License:** Apache 2.0 (Open Source)

---

## 🏆 Hacktoberfest 2026 Week 1 Takeaway

The ultimate test of an AI assistant isn't how long it keeps you on the website; it's how effectively it empowers you in the real world. By pairing open-weight AI with verified botanical data and an outdoor-first mindset, SoilMate shows how technology can inspire us to look up from our screens and touch grass.

Happy gardening, and happy Hacktoberfest! 🌱
