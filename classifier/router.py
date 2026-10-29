from pathlib import Path

from dotenv import load_dotenv
from laya import Router

try:
    from .routes import model_tier, needs_rag, reasoning_depth, vulnerable
except ImportError:  # pragma: no cover - script execution fallback
    from routes import model_tier, needs_rag, reasoning_depth, vulnerable

MODEL_DIR = Path(__file__).resolve().parents[0] / "laya_weights"
MODEL_TIER_MAP = {
    "routine": "gpt-4.1-mini",
    "advanced": "gpt-4.1",
    "deep_reasoning": "o3",
    }

load_dotenv(override=True) # prefer .env values over system environment variables

def get_recommended_model(tier: str) -> str:
    """Get the recommended model for a given tier."""
    if tier not in MODEL_TIER_MAP:
        raise ValueError(f"Unsupported model tier: {tier}. Valid tiers are: {list(MODEL_TIER_MAP.keys())}")
    return MODEL_TIER_MAP[tier]

router = Router(models={"english": str(MODEL_DIR)})
questions = {**needs_rag, **vulnerable, **model_tier, **reasoning_depth}

def route(prompt, questions=questions):
    """Select the appropriate model based on the prompt and questions."""
    result = router.predict(prompt, questions, model="english")
    return {
        question_id: result["answers"][question_id]["choice"]
        for question_id in questions
    }
