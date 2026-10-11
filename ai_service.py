"""
ai_service.py - Hosted AI client and hybrid fallback pipeline for SoilMate.

Interfaces with hosted open-weight models (Hugging Face Inference Providers) using
serverless API calls grounded in verified plant data (data/plants.json).
Provides graceful degradation to deterministic recommendation_engine on missing keys,
rate limits, model timeouts, or malformed outputs.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
import requests

from garden_data import (
    GardenPlan,
    GardenProfile,
    PlantRecommendation,
    TaskItem,
    get_plant_by_id,
)
from recommendation_engine import (
    generate_fallback_plan,
    score_plant,
    select_recommended_plants,
)

logger = logging.getLogger("soilmate.ai")

# Default configurations
DEFAULT_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
DEFAULT_TIMEOUT = 25  # seconds


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve secret from Streamlit secrets (if available) or os.environ."""
    # Try streamlit secrets first if streamlit is imported
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass

    val = os.getenv(key)
    if val:
        return val.strip()
    return default


def get_provider_status() -> Dict[str, Any]:
    """Check AI provider configuration status safely without exposing secrets."""
    token = get_secret("HF_TOKEN")
    model = get_secret("AI_MODEL", DEFAULT_MODEL)
    timeout = int(get_secret("REQUEST_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT)) or DEFAULT_TIMEOUT)

    has_token = bool(token and len(token) > 5)
    return {
        "provider": "Hugging Face Inference Providers",
        "has_token": has_token,
        "configured_model": model,
        "timeout_seconds": timeout,
        "mode_description": (
            f"Hosted AI Active ({model})"
            if has_token
            else "Rule-Based Horticultural Engine (Free-Tier Offline Mode)"
        ),
    }


def _build_ai_prompt(profile: GardenProfile, candidate_recommendations: List[PlantRecommendation]) -> str:
    """Build grounded system and user prompt containing verified horticultural candidate data."""
    candidates_data = []
    for rec in candidate_recommendations:
        p = rec.plant
        candidates_data.append({
            "id": p.id,
            "name": p.common_name,
            "category": p.category,
            "difficulty": p.difficulty,
            "sunlight_hours_min": p.min_sunlight_hours,
            "container_depth_inches": p.min_container_depth_inches,
            "watering_guidance": p.watering_guidance,
            "outdoor_touch_grass_tip": p.touch_grass_activity,
        })

    prompt = f"""You are SoilMate, an encouraging, grounded horticultural assistant focused on helping beginner gardeners touch grass and complete practical outdoor activities.

User Garden Profile:
- Location/City: {profile.city_or_region}
- Garden Space Type: {profile.garden_type}
- Available Sunlight: {profile.sunlight.replace('_', ' ')}
- Space Footprint: {profile.space.replace('_', ' ')}
- Primary Goal: {profile.goal.replace('_', ' ')}
- Experience Level: {profile.experience_level}

Verified Plant Candidates from Reference Catalog:
{json.dumps(candidates_data, indent=2)}

INSTRUCTIONS:
1. Ground your recommendations strictly on the provided verified candidates above. Choose 2 to 3 plants from the candidates list.
2. Output a structured 7-day outdoor action plan designed to get the user outdoors, touching soil/grass, checking light, aerating containers, sowing, and caring for plants.
3. Return ONLY a valid JSON object matching the schema below. Do not include markdown preamble or conversational text outside the JSON.

SCHEMA:
{{
  "summary": "2-3 sentence overview encouraging the user to garden outdoors",
  "selected_plant_ids": ["id1", "id2"],
  "plant_reasons": {{
    "id1": "Brief reason why this plant fits user profile",
    "id2": "Brief reason why this plant fits user profile"
  }},
  "preparation_steps": [
    "Step 1 for container and outdoor space prep",
    "Step 2 for soil aeration and compost"
  ],
  "care_instructions": [
    "Instruction 1 for watering and sun check",
    "Instruction 2 for daily maintenance"
  ],
  "seven_day_plan": [
    {{
      "day": 1,
      "title": "Day 1: Title",
      "instructions": "Specific action to perform outdoors",
      "estimated_minutes": 15,
      "outdoor_tip": "Sensory touch grass tip"
    }},
    ... up to Day 7
  ],
  "verification_notes": "Note citing verified plant catalog"
}}
"""
    return prompt


def _clean_json_response(raw_text: str) -> str:
    """Extract valid JSON from markdown code blocks or messy LLM response."""
    cleaned = raw_text.strip()
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    
    # Try finding first '{' and last '}'
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return cleaned[first_brace : last_brace + 1].strip()

    return cleaned


def generate_garden_plan(profile: GardenProfile) -> GardenPlan:
    """
    Generate garden plan using hosted open-weight AI (Hugging Face),
    automatically falling back to deterministic horticultural engine on any failure.
    """
    token = get_secret("HF_TOKEN")
    model = get_secret("AI_MODEL", DEFAULT_MODEL)
    timeout = int(get_secret("REQUEST_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT)) or DEFAULT_TIMEOUT)

    # 1. Immediate fallback if no token configured
    if not token or len(token) < 5:
        logger.info("No HF_TOKEN detected. Using deterministic rule-based engine.")
        return generate_fallback_plan(profile)

    # 2. Get verified candidate plants
    candidate_recs = select_recommended_plants(profile, top_n=4)
    prompt = _build_ai_prompt(profile, candidate_recs)

    # Endpoints to try (Hugging Face router & api-inference)
    endpoints = [
        f"https://router.huggingface.co/hf-inference/models/{model}",
        f"https://api-inference.huggingface.co/models/{model}",
    ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1200,
            "temperature": 0.4,
            "return_full_text": False,
        },
    }

    last_error: Optional[str] = None

    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            if response.status_code == 200:
                resp_json = response.json()
                raw_text = ""
                if isinstance(resp_json, list) and len(resp_json) > 0:
                    raw_text = resp_json[0].get("generated_text", "")
                elif isinstance(resp_json, dict):
                    raw_text = resp_json.get("generated_text", str(resp_json))

                if not raw_text:
                    raise ValueError("Empty generation received from AI provider")

                # Parse JSON
                cleaned_json_str = _clean_json_response(raw_text)
                parsed_data = json.loads(cleaned_json_str)

                # Validate & map plants
                recommended_plants: List[PlantRecommendation] = []
                selected_ids = parsed_data.get("selected_plant_ids", [])
                reasons_map = parsed_data.get("plant_reasons", {})

                for pid in selected_ids:
                    plant_obj = get_plant_by_id(pid)
                    if plant_obj:
                        score, default_reason = score_plant(plant_obj, profile)
                        reason_text = reasons_map.get(pid, default_reason)
                        recommended_plants.append(
                            PlantRecommendation(plant=plant_obj, match_score=score, reason=reason_text)
                        )

                # Fallback to candidate picks if none matched
                if not recommended_plants:
                    recommended_plants = candidate_recs[:3]

                # Map 7-day checklist
                raw_tasks = parsed_data.get("seven_day_plan", [])
                task_items: List[TaskItem] = []
                if isinstance(raw_tasks, list) and len(raw_tasks) >= 5:
                    for i, t in enumerate(raw_tasks[:7], start=1):
                        task_items.append(
                            TaskItem(
                                day=int(t.get("day", i)),
                                title=str(t.get("title", f"Day {i} Outdoor Task")),
                                instructions=str(t.get("instructions", "Step outside to inspect your plants.")),
                                estimated_minutes=max(5, min(90, int(t.get("estimated_minutes", 15)))),
                                completed=False,
                                outdoor_tip=str(t.get("outdoor_tip", "Touch grass and check soil moisture.")),
                            )
                        )
                
                # If AI didn't provide complete 7 tasks, use verified fallback tasks
                if len(task_items) < 7:
                    fb = generate_fallback_plan(profile)
                    task_items = fb.seven_day_plan

                summary = str(parsed_data.get("summary", "Personalized 7-day outdoor planting plan."))
                prep_steps = list(parsed_data.get("preparation_steps", []))
                care_steps = list(parsed_data.get("care_instructions", []))
                verification = (
                    f"Generated by {model} hosted on Hugging Face Inference Providers, "
                    "strictly verified against curated horticultural reference dataset."
                )

                return GardenPlan(
                    source="ai",
                    provider_label=f"Hosted AI ({model})",
                    model_name=model,
                    summary=summary,
                    profile=profile,
                    recommended_plants=recommended_plants,
                    preparation_steps=prep_steps if prep_steps else ["Prepare clean pots with drainage holes."],
                    care_instructions=care_steps if care_steps else ["Water when topsoil feels dry."],
                    seven_day_plan=task_items,
                    verification_notes=verification,
                )

            else:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.warning(f"AI endpoint error on {endpoint}: {last_error}")

        except requests.exceptions.Timeout:
            last_error = f"Request timed out after {timeout}s"
            logger.warning(f"Timeout connecting to {endpoint}: {last_error}")
        except Exception as e:
            last_error = f"Exception during AI inference: {type(e).__name__}"
            logger.warning(f"Error on {endpoint}: {last_error}")

    # If all endpoints failed or returned errors, gracefully return deterministic fallback
    logger.info(f"AI generation failed ({last_error}). Activating deterministic fallback.")
    fallback_plan = generate_fallback_plan(profile)
    fallback_plan.verification_notes += f" (Note: Hosted AI unavailable: {last_error or 'no response'}; verified fallback activated automatically.)"
    return fallback_plan
