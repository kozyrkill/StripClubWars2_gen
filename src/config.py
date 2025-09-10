"""
Configuration settings for SCW Character Image Generator
"""
import os
from pathlib import Path
from typing import Dict, Any, List

class Config:
    """Central configuration class"""
    
    # API Configuration
    WEBUI_URL = os.getenv("WEBUI_URL", "http://localhost:7860")
    WEBUI_API_URL = f"{WEBUI_URL}/sdapi/v1"
    
    # Image Generation Settings
    DEFAULT_STEPS = 30
    DEFAULT_CFG_SCALE = 12
    DEFAULT_SAMPLER = "DPM++ 2M Karras"
    HEADSHOT_STEPS = 40
    HEADSHOT_CFG_SCALE = 8.0
    
    # Image Sizes
    BODY_GENERATION_SIZE = (640, 1024)
    BODY_TARGET_SIZE = (512, 800)
    HEAD_GENERATION_SIZE = (360, 480)
    HEAD_TARGET_SIZE = (120, 160)
    
    # File Settings
    DEFAULT_MODKEY = "custom"
    DEFAULT_OUTPUT_DIR = "generated_characters"
    
    # Generation Settings
    DELAY_BETWEEN_GENERATIONS = 2
    MAX_RETRIES = 3
    
    # Quality Settings
    BASE_PROMPT_QUALITY = "masterpiece, best quality, high resolution, detailed, realistic, photorealistic"
    STYLE_PROMPT = "soft lighting, professional photography, clean background"
    BASE_NEGATIVE_PROMPT = (
        "low quality, blurry, distorted, deformed, ugly, bad anatomy, "
        "bad face, poorly drawn face, deformed face, ugly face, asymmetrical face, asymmetrical eyes, "
        "cross-eye, lazy eye, extra eyes, missing eyes, mutated mouth, deformed mouth, huge nose, bad teeth, "
        "extra limbs, missing limbs, watermark, signature, text, "
        "bad hands, malformed hands, extra fingers, missing fingers, "
        "cropped, cut off, incomplete body, missing legs, missing feet, "
        "half body, bust shot, torso only, upper body only, portrait crop, "
        "multiple people, two people, extra person, duplicate person, group, crowd, more than one person"
    )

class PromptTemplates:
    """Prompt templates and mappings"""
    
    GENDER_PROMPTS = {
        "f": "beautiful woman, female",
        "m": "handsome man, male"
    }
    
    AGE_PROMPTS = {
        1: "young adult, 20 years old",
        2: "young adult, 25 years old", 
        3: "adult, 35 years old",
        4: "middle-aged, 45 years old",
        5: "mature, 55 years old"
    }
    
    ETHNICITY_PROMPTS = {
        "w": "caucasian, white skin",
        "b": "african american, dark skin",
        "h": "hispanic, latin, medium skin tone",
        "a": "asian, light skin",
        "r": "middle eastern, medium skin tone"
    }
    
    BODY_SHAPE_PROMPTS = {
        "s": "slim body, skinny",
        "n": "normal body type, average build",
        "c": "curvy body, voluptuous",
        "f": "fit body, athletic, muscular"
    }
    
    HAIR_COLOR_PROMPTS = {
        "l": "blonde hair, light hair",
        "m": "brown hair, medium hair color",
        "d": "dark hair, black hair"
    }
    
    HAIR_LENGTH_PROMPTS = {
        "b": "bald, no hair",
        "s": "short hair",
        "m": "medium length hair",
        "l": "long hair"
    }
    
    # Full body emphasis prompts
    FULL_BODY_PROMPT = (
        "full body, full shot, long shot, complete figure visible, whole person visible, "
        "from head to feet, legs and feet visible, feet on ground, no cropping, "
        "entire body in frame, standing full height"
    )
    
    # Anti-cropping negative prompts for nude/semi-nude poses
    ANTI_CROPPING_NEGATIVES = (
        "crossed legs, legs crossed, closed legs, knees together, legs together, "
        "ankles together, thighs together, pressed thighs, knees closed, legs tightly closed, "
        "legs pressed together, thighs pressed together, knees touching, ankles touching, "
        "legs side by side, thighs side by side"
    )

class PoseConfig:
    """Pose configuration and mappings"""
    
    POSES_CONFIG = {
        "head": {"reveal_variants": [0], "required": True, "description": "headshot portrait"},
        "cas": {"reveal_variants": [0, 1, 2], "required": True, "description": "casual outfit"},
        "uw": {"reveal_variants": [3, 4, 5], "required": True, "description": "underwear/lingerie"},
        "nude": {"reveal_variants": [9, 10, 11], "required": True, "description": "nude"},
        "bc": {"reveal_variants": [0, 1], "required": False, "description": "business casual"},
        "biz": {"reveal_variants": [0, 1], "required": False, "description": "business formal"},
        "fun": {"reveal_variants": [0, 1, 2], "required": False, "description": "fun/active wear"},
        "tl": {"reveal_variants": [6, 7, 8], "required": False, "description": "topless", "female_only": True},
        "ss": {"reveal_variants": [2, 3, 4], "required": False, "description": "swimsuit", "female_only": True},
        "s1": {"reveal_variants": [1, 2, 3], "required": False, "description": "stripper outfit 1", "female_only": True},
        "s2": {"reveal_variants": [3, 4, 5], "required": False, "description": "stripper outfit 2", "female_only": True},
        "s3": {"reveal_variants": [5, 6, 7], "required": False, "description": "stripper outfit 3", "female_only": True},
        "preg": {"reveal_variants": [0, 1, 2], "required": False, "description": "pregnant", "female_only": True},
    }
    
    # Alias mappings for pose compatibility
    POSE_ALIAS_MAP = {
        "business": "biz",
        "bizcas": "bc",
        "strip1": "s1",
        "strip2": "s2", 
        "strip3": "s3"
    }
    
    POSE_PROMPTS = {
        "head": "close-up portrait, headshot, face centered, looking at viewer, studio lighting, beauty lighting, soft light, smooth skin, detailed eyes, catchlight in eyes, symmetrical face, both eyes visible, face in frame, no obstruction",
        "cas": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure",
        "uw": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure", 
        "bc": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure",
        "biz": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure",
        "fun": "full body, full body shot, head to toe, legs visible, feet visible, active pose, complete figure",
        "tl": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, topless, bare chest, exposed breasts, no shirt, no top",
        "nude": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, nude, naked, no clothes, without clothing, no outfit, no lingerie, no bra, no panties",
        "ss": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure",
        "s1": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, sexy, seductive",
        "s2": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, sexy, seductive", 
        "s3": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, sexy, seductive",
        "preg": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure"
    }

def load_user_config(config_path: str = None) -> Dict[str, Any]:
    """Load user configuration from file if it exists"""
    if config_path and Path(config_path).exists():
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}
