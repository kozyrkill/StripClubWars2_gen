#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCW Character Image Pack Generator

Generates character image packs for Strip Club Wars 2

Uses Stable Diffusion WebUI API to generate character images
and post-processes them to meet game requirements.
"""

import os
import json
import requests
import io
import base64
from PIL import Image, ImageOps
from rembg import remove
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import time
import random
import datetime

# Stable Diffusion WebUI configuration
WEBUI_URL = "http://localhost:7860"
WEBUI_API_URL = f"{WEBUI_URL}/sdapi/v1"

@dataclass
class CharacterAttributes:
    """Character attributes for generation"""
    # Required attributes (reqphys)
    gender: str  # m/f
    age_group: int  # 1-5 (18-24, 22-31, 28-42, 38-51, 48+)
    ethnicity: str  # w/b/h/a/r (white, black, hispanic, asian, middle-eastern)
    
    # Optional attributes (optphys)
    height: str = "m"  # t/m/s (tall, medium, short)
    body_shape: str = "n"  # s/n/c/f (slim, normal, curvy, fit)
    hips_size: str = "m"  # s/m/l (small, medium, large)
    breast_penis_size: str = "m"  # s/m/l/h/x (tiny, small, medium, large, huge, extra-huge)
    skin_tone: str = "l"  # l/m/d (light, medium, dark)
    
    # Image attributes (imgphys)
    hair_color: str = "m"  # l/m/d (light, medium, dark)
    hair_length: str = "m"  # b/s/m/l (bald, short, medium, long)
    eye_color: str = "m"  # l/m/d (light, medium, dark)
    
    # Additional details for consistency
    hair_style: str = "n"  # n/s/c/w (normal, straight, curly, wavy)
    facial_hair: str = "n"  # n/m/b/f (none, mustache, beard, full_beard) - males only
    makeup: str = "n"  # n/l/m/h (none, light, medium, heavy) - females only
    tattoos: str = "n"  # n/s/m/l (none, small, medium, large)
    piercings: str = "n"  # n/e/o/m (none, ears, nose, multiple)
    expression: str = "n"  # n/s/h/f (neutral, smile, happy, flirty)
    clothing_style: str = "c"  # c/e/g/s (casual, elegant, gothic, sporty)

# Poses configuration with reveal variants (supports multiple variants)
POSES_CONFIG = {
    # Base poses for all characters
    "head": {"reveal_variants": [0], "required": True, "description": "headshot"},
    "cas": {"reveal_variants": [0, 1, 2], "required": True, "description": "casual clothes"},
    "uw": {"reveal_variants": [3, 4, 5], "required": True, "description": "underwear"},
    "nude": {"reveal_variants": [9, 10, 11], "required": True, "description": "nude"},
    
    # Additional poses
    "bc": {"reveal_variants": [0, 1], "required": False, "description": "business casual"},
    "biz": {"reveal_variants": [0, 1], "required": False, "description": "business suit"},
    "fun": {"reveal_variants": [0, 1, 2], "required": False, "description": "fun/workout clothes"},

    # Aliases for engine compatibility
    "bizcas": {"reveal_variants": [0, 1], "required": False, "description": "business casual (alias of bc)"},
    "business": {"reveal_variants": [0, 1], "required": False, "description": "business (alias of biz)"},
    
    # Female-only
    "tl": {"reveal_variants": [6, 7, 8], "required": False, "description": "topless", "female_only": True},
    "ss": {"reveal_variants": [2, 3, 4], "required": False, "description": "swimsuit", "female_only": True},
    "s1": {"reveal_variants": [1, 2, 3], "required": False, "description": "stripper outfit 1", "female_only": True},
    "s2": {"reveal_variants": [3, 4, 5], "required": False, "description": "stripper outfit 2", "female_only": True},
    "s3": {"reveal_variants": [5, 6, 7], "required": False, "description": "stripper outfit 3", "female_only": True},
    "preg": {"reveal_variants": [1, 3, 6], "required": False, "description": "pregnant", "female_only": True},
    
    # Alias stripper codes
    "strip2": {"reveal_variants": [3, 4, 5], "required": False, "description": "stripper outfit 2 (alias of s2)", "female_only": True},
    "strip3": {"reveal_variants": [5, 6, 7], "required": False, "description": "stripper outfit 3 (alias of s3)", "female_only": True},
}

# Pose alias map for compatibility with engines expecting alternative codes
POSE_ALIAS_MAP = {
    "business": "biz",
    "bizcas": "bc",
    "strip1": "s1",
    "strip2": "s2",
    "strip3": "s3",
}

# Dictionaries for translating attributes to prompts
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

POSE_PROMPTS = {
    "head": "close-up portrait, headshot, face centered, looking at viewer, studio lighting, beauty lighting, soft light, smooth skin, detailed eyes, catchlight in eyes, symmetrical face, both eyes visible, face in frame, no obstruction",
    "cas": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure",
    "bc": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure", 
    "biz": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure",
    "fun": "full body, full body shot, head to toe, legs visible, feet visible, active pose, complete figure",
    "uw": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure",
    "ss": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure",
    "tl": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, topless, bare chest, exposed breasts, no shirt, no top",
    "nude": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, nude, naked, no clothes, without clothing, no outfit, no lingerie, no bra, no panties",
    "s1": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, sexy, seductive",
    "s2": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, sexy, seductive", 
    "s3": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure, sexy, seductive",
    "preg": "full body, full body shot, head to toe, legs visible, feet visible, standing pose, complete figure"
}

# New dictionaries for additional details
HAIR_STYLE_PROMPTS = {
    "n": "natural hair",
    "s": "straight hair",
    "c": "curly hair, curls",
    "w": "wavy hair, waves"
}

FACIAL_HAIR_PROMPTS = {
    "n": "",  # no facial hair
    "m": "mustache",
    "b": "beard, facial hair",
    "f": "full beard, heavy facial hair"
}

MAKEUP_PROMPTS = {
    "n": "natural look, no makeup",
    "l": "light makeup, subtle",
    "m": "makeup, cosmetics",
    "h": "heavy makeup, glamorous"
}

TATTOO_PROMPTS = {
    "n": "",  # no tattoos
    "s": "small tattoo",
    "m": "tattoos, body art",
    "l": "many tattoos, heavily tattooed"
}

PIERCINGS_PROMPTS = {
    "n": "",  # no piercings
    "e": "ear piercings",
    "o": "nose piercing",
    "m": "multiple piercings, facial piercings"
}

EXPRESSION_PROMPTS = {
    "n": "neutral expression",
    "s": "slight smile, smiling",
    "h": "happy, joyful expression",
    "f": "flirty, seductive expression"
}

CLOTHING_STYLE_PROMPTS = {
    "c": "casual style",
    "e": "elegant style, refined",
    "g": "gothic style, dark aesthetic",
    "s": "sporty style, athletic wear"
}

class SCWImageGenerator:
    """SCW image generator"""
    
    def __init__(self, output_dir: str = "generated_characters", modkey: str = "custom"):
        self.output_dir = Path(output_dir)
        self.modkey = modkey
        
        # Create a new session directory based on timestamp and prefix with modkey
        session_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"{self.modkey}_{session_timestamp}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Session: {self.session_dir.name}")
        
    def check_webui_connection(self) -> bool:
        """Check connection to Stable Diffusion WebUI"""
        try:
            response = requests.get(f"{WEBUI_API_URL}/options")
            return response.status_code == 200
        except:
            return False
    
    def generate_character_id(self, character: CharacterAttributes) -> str:
        """Generate random character ID based on current time"""
        # Use current time in microseconds for uniqueness
        timestamp = int(time.time() * 1000000)  # microseconds
        random_part = random.randint(100, 999)  # add randomness
        
        if character.gender == "f":
            # Females: last 5 digits (0-49999)
            char_id = f"{(timestamp + random_part) % 50000:05d}"
        else:
            # Males: 10000 + last 4 digits
            char_id = f"{10000 + (timestamp + random_part) % 10000:05d}"
        
        return char_id
    
    def generate_character_seed(self, char_id: str) -> int:
        """Generates a persistent seed for the character based on its ID"""
        # Use hash of ID to get a persistent seed
        import hashlib
        hash_obj = hashlib.md5(f"{self.modkey}-{char_id}".encode())
        # Take first 8 bytes of hash and convert to int (max for SD seed)
        seed = int(hash_obj.hexdigest()[:8], 16) % (2**31 - 1)  # Limit to 31 bits
        return seed
    
    def build_base_prompt(self, character: CharacterAttributes) -> str:
        """Creates a base prompt for the character with all details"""
        prompt_parts = []
        
        # Main characteristics
        prompt_parts.append(GENDER_PROMPTS[character.gender])
        prompt_parts.append(AGE_PROMPTS[character.age_group])
        prompt_parts.append(ETHNICITY_PROMPTS[character.ethnicity])
        
        # Body shape
        prompt_parts.append(BODY_SHAPE_PROMPTS[character.body_shape])
        
        # Hair (main)
        prompt_parts.append(HAIR_COLOR_PROMPTS[character.hair_color])
        prompt_parts.append(HAIR_LENGTH_PROMPTS[character.hair_length])
        
        # Hair style
        hair_style_prompt = HAIR_STYLE_PROMPTS.get(character.hair_style, "")
        if hair_style_prompt:
            prompt_parts.append(hair_style_prompt)
        
        # Eyes
        if character.eye_color in ["l", "d"]:  # only if not default
            prompt_parts.append(f"{character.eye_color} eyes")
        
        # Facial expression
        expression_prompt = EXPRESSION_PROMPTS.get(character.expression, "")
        if expression_prompt:
            prompt_parts.append(expression_prompt)
        
        # Facial hair (males only)
        if character.gender == "m" and character.facial_hair != "n":
            facial_hair_prompt = FACIAL_HAIR_PROMPTS.get(character.facial_hair, "")
            if facial_hair_prompt:
                prompt_parts.append(facial_hair_prompt)
        
        # Makeup (females only)
        if character.gender == "f" and character.makeup != "n":
            makeup_prompt = MAKEUP_PROMPTS.get(character.makeup, "")
            if makeup_prompt:
                prompt_parts.append(makeup_prompt)
        
        # Tattoos
        if character.tattoos != "n":
            tattoo_prompt = TATTOO_PROMPTS.get(character.tattoos, "")
            if tattoo_prompt:
                prompt_parts.append(tattoo_prompt)
        
        # Piercings
        if character.piercings != "n":
            piercing_prompt = PIERCINGS_PROMPTS.get(character.piercings, "")
            if piercing_prompt:
                prompt_parts.append(piercing_prompt)
        
        # Body size details
        if character.breast_penis_size == "s":
            if character.gender == "f":
                prompt_parts.append("small breasts, tiny chest, petite bust")
            else:
                prompt_parts.append("slim build")
        elif character.breast_penis_size == "l":
            if character.gender == "f":
                prompt_parts.append("large breasts, big bust")
            else:
                prompt_parts.append("athletic build, muscular")
        elif character.breast_penis_size == "h":
            if character.gender == "f":
                prompt_parts.append("huge breasts, very large bust")
            else:
                prompt_parts.append("very muscular, strong build")
        elif character.breast_penis_size == "x":
            if character.gender == "f":
                prompt_parts.append("extra huge breasts, gigantic bust, massive boobs")
            else:
                prompt_parts.append("extremely muscular, bodybuilder")
        
        # Clothing style (applies to clothing poses)
        if hasattr(character, 'clothing_style') and character.clothing_style != "c":
            style_prompt = CLOTHING_STYLE_PROMPTS.get(character.clothing_style, "")
            if style_prompt:
                prompt_parts.append(style_prompt)
        
        return ", ".join(filter(None, prompt_parts))  # filter empty parts
    
    def get_footwear_description(self, pose: str, reveal_level: int, gender: Optional[str] = None) -> str:
        """Returns footwear and stockings description for a pose and reveal level (gender-aware)."""
        eff_pose = POSE_ALIAS_MAP.get(pose, pose)
        footwear_variants = {
            "cas": {0: "white sneakers, cotton socks", 1: "stylish sneakers, ankle socks", 2: "fashionable boots, bare legs"},
            "bc": {0: "black office shoes, nude pantyhose", 1: "high heels, sheer stockings", 2: "stiletto heels, lace-top stockings"},
            "biz": {0: "conservative black pumps, professional pantyhose", 1: "elegant heels, nude stockings", 2: "sexy high heels, seductive stockings"},
            "uw": {3: "bare feet, no socks", 4: "thigh-high stockings, bare feet", 5: "sexy stockings with garters, bare feet"},
            "ss": {2: "bare feet, swimming attire", 3: "beach sandals or bare feet", 4: "bare feet, minimal swimwear"},
            "fun": {0: "athletic shoes, sports socks", 1: "running shoes, ankle socks", 2: "gym shoes, athletic wear"},
            "tl": {6: "high heels", 7: "stiletto heels", 8: "platform heels"},
            "s1": {1: "high heels", 2: "stiletto heels", 3: "platform heels"},
            "s2": {3: "platform heels", 4: "stiletto heels", 5: "platform heels, ankle strap"},
            "s3": {5: "platform heels", 6: "stiletto heels", 7: "platform heels, ankle strap"},
        }
        # Male overrides (use effective pose)
        if gender == 'm':
            male_overrides = {
                "bc": {0: "black dress shoes", 1: "black dress shoes", 2: "black dress shoes"},
                "biz": {0: "oxford dress shoes", 1: "oxford dress shoes", 2: "oxford dress shoes"},
                "uw": {3: "bare feet", 4: "bare feet", 5: "bare feet"},
                "ss": {2: "bare feet", 3: "flip flops", 4: "bare feet"},
                "tl": {6: "bare feet", 7: "bare feet", 8: "bare feet"},
                "s1": {1: "bare feet", 2: "bare feet", 3: "bare feet"},
                "s2": {3: "bare feet", 4: "bare feet", 5: "bare feet"},
                "s3": {5: "bare feet", 6: "bare feet", 7: "bare feet"},
            }
            if eff_pose in male_overrides and reveal_level in male_overrides[eff_pose]:
                return male_overrides[eff_pose][reveal_level]
        pose_footwear = footwear_variants.get(eff_pose, {})
        footwear = pose_footwear.get(reveal_level, "")
        if not footwear:
            general_footwear = {0: "modest shoes, regular socks", 1: "stylish footwear", 2: "fashionable shoes", 3: "attractive footwear", 4: "sexy shoes, stockings", 5: "seductive footwear", 9: "bare feet"}
            footwear = general_footwear.get(reveal_level, "appropriate footwear")
        return footwear

    def get_clothing_description(self, pose: str, reveal_level: int, gender: Optional[str] = None) -> str:
        """Return full clothing description including footwear for pose and reveal level (gender-aware)"""
        eff_pose = POSE_ALIAS_MAP.get(pose, pose)
        if eff_pose == "nude":
            return "no clothing, fully nude, bare skin, no outfit, no lingerie, hairless pubic area, bare feet"
        # Female-oriented
        clothing_variants_f = {
            "cas": {0: "blue jeans and white t-shirt, casual everyday outfit", 1: "fitted dark jeans and tight colorful top, stylish casual", 2: "short denim skirt and crop top, trendy casual showing some skin"},
            "bc": {0: "white business blouse and dark pants, conservative professional attire", 1: "fitted gray blazer and pencil skirt, professional but elegant", 2: "partially unbuttoned blouse and tight skirt, business casual revealing"},
            "biz": {0: "dark business suit with jacket and pants, formal conservative wear", 1: "fitted navy suit with short skirt, professional attractive look", 2: "open suit jacket with tight blouse and mini skirt, formal revealing"},
            "uw": {3: "matching white cotton bra and panties, classic lingerie set", 4: "black lacy bra and panties, elegant semi-transparent underwear, sheer mesh panels", 5: "red silk lingerie set, barely covering, seductive underwear, see-through mesh, semi-transparent"},
            "ss": {2: "blue one-piece swimsuit, modest athletic swimming attire", 3: "colorful bikini top and bottom, classic two-piece beachwear, sheer mesh panels", 4: "tiny string bikini, minimal coverage, revealing swimwear, semi-transparent elements"},
            "tl": {6: "topless, panties only (thong or g-string), no top, exposed breasts", 7: "topless, micro skirt or shorts with exposed breasts, no bra", 8: "topless, sheer lace panties or mesh bottoms, exposed breasts, no bra"},
            "s1": {1: "sparkly sequined mini dress, fishnet stockings, sheer mesh panels", 2: "tight mini dress with deep neckline, thigh-high stockings, garter belt, semi-transparent", 3: "corset top with short skirt, fishnets, feather boa, rhinestones, see-through details"},
            "s2": {3: "black corset and g-string, garter belt, fishnet stockings, gloves, sheer mesh", 4: "latex mini dress, thigh-high stockings, platform heels, choker, semi-transparent sections", 5: "pasties and g-string, garter belt, fishnets, feather boa, glitter, see-through elements"},
            "s3": {5: "micro bikini top and thong, fishnets, garter belt, high heels, glitter, transparent mesh", 6: "strappy lingerie harness, g-string, thigh-highs, platform heels, rhinestones, see-through", 7: "nipple pasties, g-string, body glitter, feather boa, high heels, semi-transparent mesh"},
        }
        # Male-oriented
        clothing_variants_m = {
            "cas": {0: "jeans and t-shirt, casual outfit", 1: "fitted t-shirt and jeans, casual wear", 2: "shorts and tank top, casual sportswear"},
            "bc": {0: "button-up shirt and slacks, conservative professional", 1: "fitted shirt and slacks, business casual", 2: "open collar shirt and fitted slacks, stylish business casual"},
            "biz": {0: "business suit with tie, formal wear", 1: "fitted suit, no tie, professional", 2: "open jacket, fitted shirt and pants, formal"},
            "uw": {3: "boxers", 4: "briefs", 5: "boxer briefs"},
            "ss": {2: "swim trunks", 3: "board shorts", 4: "speedo swim briefs"},
        }
        if gender == 'm' and eff_pose in clothing_variants_m:
            clothing_desc = clothing_variants_m[eff_pose].get(reveal_level, "appropriate clothing")
        else:
            clothing_desc = clothing_variants_f.get(eff_pose, {}).get(reveal_level, "appropriate clothing")
        footwear_desc = self.get_footwear_description(eff_pose, reveal_level, gender)
        return f"{clothing_desc}, {footwear_desc}"
    
    def build_pose_prompt(self, base_prompt: str, pose: str, reveal_level: int = 0, variant_idx: int = 0, gender: Optional[str] = None) -> str:
        """Create pose-specific prompt with clothing description and full-body emphasis."""
        eff_pose = POSE_ALIAS_MAP.get(pose, pose)
        pose_base = POSE_PROMPTS.get(eff_pose, "")
        clothing_desc = self.get_clothing_description(eff_pose, reveal_level, gender)
        # Pose diversification
        variant_descriptors_by_pose = {
            "nude": [
                "natural stance, relaxed arms, subtle smile, legs apart, shoulder-width stance, clear pelvis visibility, detailed anatomy, erotic pose",
                "arms on hips, confident posture, looking at viewer, front view pelvis visible, legs apart, provocative pose",
                "one hand behind head, playful smile, slight hip tilt, pelvis unobstructed, no pubic hair, legs apart, seductive pose",
                "3/4 view, looking over shoulder, soft smile, smooth skin, hairless pubic area, wide stance, sensual pose",
                "contrapposto pose, one leg forward, elegant posture, detailed pelvis region, open-legged stance, arched back",
                "hands gently at sides, neutral expression, relaxed, anatomically correct details, legs apart, hips forward",
                "back view, looking over shoulder at camera, legs apart, sensual pose",
                "side profile, legs apart, hands on hips, confident gaze"
            ],
            "tl": [
                "arms crossed under chest, subtle smile, topless emphasized, exposed breasts",
                "one arm behind head, other on hip, playful, bare chest visible, exposed breasts",
                "hands on hips, confident, looking at viewer, no top, no bra, exposed breasts",
                "3/4 view, hair over shoulder, topless emphasized",
                "side profile, chest turned to camera, topless emphasized"
            ],
            "cas": [
                "standing straight, hands at sides",
                "one leg forward, casual stance",
                "hands in pockets, relaxed",
                "leaning slightly, weight on one leg, casual smile",
                "3/4 view, looking over shoulder, casual pose",
                "side profile, head turned to camera",
                "arms crossed, relaxed posture",
                "hand on hip, confident casual stance"
            ],
            "bc": [
                "hands clasped in front, professional posture",
                "one hand on hip, slight smile, professional",
                "3/4 view, looking at viewer, confident",
                "arms crossed, business casual stance",
                "side profile, head turned to camera",
                "leaning slightly forward, friendly smile"
            ],
            "biz": [
                "standing straight, formal posture",
                "one hand adjusting jacket, professional",
                "hands behind back, confident stance",
                "3/4 view, looking at viewer",
                "side profile, head turned to camera",
                "arms crossed, formal look"
            ],
            "fun": [
                "hands on hips, playful smile",
                "one arm raised, casual vibe",
                "slight hip tilt, relaxed pose",
                "3/4 view, looking at viewer, fun expression",
                "side profile, sporty stance",
                "hands behind back, cheerful"
            ],
            "uw": [
                "hands on hips, confident look",
                "one hand behind head, playful",
                "3/4 view, looking at viewer",
                "side profile, head turned to camera",
                "arms crossed below chest, soft smile"
            ],
            "ss": [
                "hands on hips, beach vibe",
                "one hand adjusting hair, smiling",
                "3/4 view, looking at viewer, relaxed",
                "side profile, head turned to camera",
                "arms behind back, cheerful"
            ],
            "s1": [
                "sexy pose, hip tilt, playful smile, semi-transparent outfit",
                "one hand on thigh, other on hip, seductive gaze, see-through mesh",
                "back arched, chest forward, provocative stance, sheer fabric",
                "3/4 view, looking at viewer, flirty",
                "side profile, hand on thigh, alluring"
            ],
            "s2": [
                "corset emphasized, garter belt visible, seductive smile, sheer panels",
                "hip sway, hand sliding on thigh, erotic pose, transparent mesh",
                "leaning slightly forward, inviting gaze, semi-transparent latex",
                "3/4 view, looking at viewer, provocative",
                "side profile, arched back, alluring"
            ],
            "s3": [
                "hands on hips, confident look, body glitter, see-through mesh",
                "one hand behind head, other pointing down, provocative, transparent elements",
                "leg lifted slightly on toe, arched back, seductive, semi-transparent",
                "3/4 view, looking at viewer, flirty",
                "side profile, hand on hip, alluring"
            ],
        }
        pose_variants = variant_descriptors_by_pose.get(eff_pose, [])
        pose_variant_desc = pose_variants[variant_idx % len(pose_variants)] if pose_variants else ""
        # Quality
        quality_prompt = "masterpiece, best quality, high resolution, detailed, realistic, photorealistic"
        # Full-body emphasis
        if eff_pose != "head":
            full_body_emphasis = (
                "full body, full shot, long shot, complete figure visible, whole person visible, "
                "from head to feet, legs and feet visible, feet on ground, no cropping, "
                "entire body in frame, standing full height"
            )
            if eff_pose == "nude":
                full_body_emphasis = f"{full_body_emphasis}, legs apart, open-legged stance, hips forward, arched back"
        else:
            full_body_emphasis = "tight headshot, face fills frame"
        style_prompt = "soft lighting, professional photography, clean background"
        prompt_parts = [full_body_emphasis if eff_pose != "head" else "", quality_prompt, base_prompt, pose_base, clothing_desc, pose_variant_desc, style_prompt]
        return ", ".join(filter(None, prompt_parts))
    
    def generate_negative_prompt(self, pose: Optional[str] = None, gender: Optional[str] = None) -> str:
        """Create negative prompt (pose- and gender-aware)."""
        base = (
            "low quality, blurry, distorted, deformed, ugly, bad anatomy, "
            "bad face, poorly drawn face, deformed face, ugly face, asymmetrical face, asymmetrical eyes, cross-eye, lazy eye, extra eyes, missing eyes, mutated mouth, deformed mouth, huge nose, bad teeth, "
            "extra limbs, missing limbs, watermark, signature, text, "
            "bad hands, malformed hands, extra fingers, missing fingers, "
            "cropped, cut off, incomplete body, missing legs, missing feet, "
            "half body, bust shot, torso only, upper body only, portrait crop, "
            "multiple people, two people, extra person, duplicate person, group, crowd, more than one person"
        )
        clothing_tokens = "clothes, outfit, lingerie, bra, panties, dress, skirt, bikini, g-string, pasties, garter, stockings, fishnets"
        female_anatomy = "vulva, vagina, labia, clitoris, areolae"
        male_anatomy = "penis, testicles, scrotum"
        if pose in ("cas", "bc", "biz", "fun", "ss"):
            base = f"{base}, {female_anatomy}, {male_anatomy}"
        if pose == "uw":
            base = f"{base}, {female_anatomy if gender=='m' else male_anatomy}"
        if pose == "tl":
            base = f"{base}, bottomless, explicit genitals, {male_anatomy}"
        if pose == "nude":
            base = f"{base}, {clothing_tokens}"
            if gender == 'm':
                base = f"{base}, {female_anatomy}"
            elif gender == 'f':
                base = f"{base}, {male_anatomy}"
        if pose in ("nude", "tl", "uw", "s1", "s2", "s3", "ss"):
            base = (
                f"{base}, crossed legs, legs crossed, closed legs, knees together, legs together, "
                "ankles together, thighs together, pressed thighs, knees closed, legs tightly closed"
            )
        return base
    
    def call_stable_diffusion_api(self, prompt: str, is_headshot: bool = False, seed: int = -1, pose: Optional[str] = None, gender: Optional[str] = None) -> Optional[Image.Image]:
        """Call Stable Diffusion WebUI txt2img API."""
        
        # Image sizes
        width = 360 if is_headshot else 640
        height = 480 if is_headshot else 1024
        
        steps = 40 if is_headshot else 34
        cfg_scale = 8.0 if is_headshot else 8.0
        
        payload = {
            "prompt": prompt,
            "negative_prompt": self.generate_negative_prompt(POSE_ALIAS_MAP.get(pose, pose), gender),
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_name": "DPM++ 2M Karras",
            "batch_size": 1,
            "n_iter": 1,
            "seed": seed,
            "restore_faces": True,
        }
        
        try:
            response = requests.post(f"{WEBUI_API_URL}/txt2img", json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("images"):
                    # Decode base64 image
                    image_data = base64.b64decode(result["images"][0])
                    return Image.open(io.BytesIO(image_data))
            return None
        except Exception as e:
            print(f"Image generation error: {e}")
            return None
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background from image"""
        try:
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Remove background via rembg
            output = remove(image)
            return output
        except Exception as e:
            print(f"Background removal error: {e}")
            # Return original image on error
            return image
    
    def postprocess_headshot(self, image: Image.Image) -> Image.Image:
        """Downscales headshot to 120x160 with high quality"""
        try:
            target_size = (120, 160)
            return image.resize(target_size, Image.LANCZOS)
        except Exception:
            return image
    
    def postprocess_body(self, image: Image.Image) -> Image.Image:
        """Downscale body image to 512x800 with high-quality resampling."""
        try:
            target_size = (512, 800)
            return image.resize(target_size, Image.LANCZOS)
        except Exception:
            return image
    
    def generate_filename(self, character: CharacterAttributes, char_id: str, pose: str, 
                         reveal_level: int = 0) -> str:
        """Generates filename following SCW format"""
        
        if pose == "head":
            # Head format: modkey-id-reqphys-optphys-imgphys-special-head.png
            reqphys = f"{character.gender}{character.age_group}{character.ethnicity}"
            optphys = f"{character.height}{character.body_shape}{character.hips_size}{character.breast_penis_size}{character.skin_tone}"
            imgphys = f"{character.hair_color}{character.hair_length}{character.eye_color}"
            special = "u"  # regular character
            
            filename = f"{self.modkey}-{char_id}-{reqphys}-{optphys}-{imgphys}-{special}-head.png"
        else:
            # Other poses format: modkey-id-reveal-pose.png
            filename = f"{self.modkey}-{char_id}-z{reveal_level}-{pose}.png"
        
        return filename
    
    def generate_character_images(self, character: CharacterAttributes, poses: List[str] = None) -> Dict[str, str]:
        """Generates all images for a character with multiple variants"""
        
        if poses is None:
            # Generate all required poses
            poses = [pose for pose, config in POSES_CONFIG.items() if config.get("required", False)]
            # Also include standard optional daily wear
            poses += ["bc", "biz", "fun", "bizcas", "business"]
            # Add female-only poses if character is female
            if character.gender == "f":
                poses += ["tl", "ss", "s1", "s2", "s3", "strip2", "strip3"]
        
        char_id = self.generate_character_id(character)
        character_seed = self.generate_character_seed(char_id)
        base_prompt = self.build_base_prompt(character)
        
        print(f"Generating character {char_id} (seed: {character_seed})")
        print(f"  Attributes: gender={character.gender}, age_group={character.age_group}, ethnicity={character.ethnicity}")
        print(f"  Variety via clothing per reveal level")
        
        generated_files = {}
        
        for pose in poses:
            # Skip female-only poses for male characters
            if POSES_CONFIG[pose].get("female_only", False) and character.gender == "m":
                continue
                
            print(f"  Pose: {pose}")
            
            # Reveal variants for this pose
            reveal_variants = POSES_CONFIG[pose].get("reveal_variants", [0])
            pose_files = []
            
            for variant_idx, reveal_level in enumerate(reveal_variants):
                print(f"    Variant {variant_idx + 1}/{len(reveal_variants)} (reveal level: {reveal_level})")
                
                # Build prompt for this pose and reveal level
                full_prompt = self.build_pose_prompt(base_prompt, pose, reveal_level, variant_idx, character.gender)
                clothing_desc = self.get_clothing_description(pose, reveal_level, character.gender)
                print(f"      Clothing: {clothing_desc}")
                
                # Log full prompts
                print(f"      📝 FULL PROMPT:")
                print(f"         {full_prompt}")
                print(f"      📝 NEGATIVE PROMPT:")
                print(f"         {self.generate_negative_prompt()}")
                
                # Generate image with persistent seed
                is_headshot = pose == "head"
                image = self.call_stable_diffusion_api(full_prompt, is_headshot, character_seed, pose, character.gender)
                
                if image:
                    # Post-process headshot/body
                    if is_headshot:
                        image = self.postprocess_headshot(image)
                    else:
                        image = self.postprocess_body(image)
                        image = self.remove_background(image)
                    
                    # Build filename and save
                    filename = self.generate_filename(character, char_id, pose, reveal_level)
                    filepath = self.session_dir / filename
                    
                    image.save(filepath, "PNG")
                    pose_files.append(str(filepath))
                    
                    print(f"      Saved: {filename}")
                    
                    # Small delay between generations
                    time.sleep(1)
                else:
                    print(f"      Variant generation error {variant_idx + 1}")
            
            if pose_files:
                generated_files[pose] = pose_files
                print(f"    ✅ Created {len(pose_files)} variants for pose {pose}")
            else:
                print(f"    ❌ Failed to create any variants for pose {pose}")
        
        return generated_files

    def load_characters_from_config(self, config_file: str) -> List[CharacterAttributes]:
        """Load characters from JSON configuration"""
        characters = []
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for preset in config.get("character_presets", []):
                character = CharacterAttributes(
                    gender=preset["gender"],
                    age_group=preset["age_group"],
                    ethnicity=preset["ethnicity"],
                    height=preset.get("height", "m"),
                    body_shape=preset.get("body_shape", "n"),
                    hips_size=preset.get("hips_size", "m"),
                    breast_penis_size=preset.get("breast_penis_size", "m"),
                    skin_tone=preset.get("skin_tone", "l"),
                    hair_color=preset.get("hair_color", "m"),
                    hair_length=preset.get("hair_length", "m"),
                    eye_color=preset.get("eye_color", "m")
                )
                characters.append(character)
                
        except Exception as e:
            print(f"Config load error: {e}")
            return self.create_sample_characters()
            
        return characters
    
    def create_sample_characters(self) -> List[CharacterAttributes]:
        """Create sample characters for testing"""
        characters = []
        
        characters.append(CharacterAttributes(
            gender="f", age_group=0, ethnicity="w",
            body_shape="s", breast_penis_size="s"
        ))
        
        characters.append(CharacterAttributes(
            gender="f", age_group=2, ethnicity="w", 
            body_shape="c", breast_penis_size="x"
        ))
        
        characters.append(CharacterAttributes(
            gender="m", age_group=4, ethnicity="a",
            body_shape="f", breast_penis_size="l"
        ))
        
        return characters
        
    def load_test_characters(self, test_type: str = "simple") -> List[CharacterAttributes]:
        """Load test characters from JSON file"""
        try:
            with open("configs/test_characters.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Select the desired character set
            if test_type == "simple":
                character_data = data.get("simple_characters", [])
            elif test_type == "detailed":
                character_data = data.get("detailed_characters", [])
            elif test_type == "extreme":
                character_data = data.get("extreme_characters", [])
            else:
                character_data = data.get("simple_characters", [])
            
            characters = []
            for char_dict in character_data:
                character = CharacterAttributes(**char_dict)
                characters.append(character)
                
            return characters
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ configs/test_characters.json load error: {e}")
            print("Falling back to built-in sample characters")
            return self.create_sample_characters()

def main():
    """Entry point"""
    parser = argparse.ArgumentParser(description="SCW Character Image Generator")
    parser.add_argument("--output-dir", default="generated_characters", 
                       help="Directory to save generated images")
    parser.add_argument("--modkey", default="custom", 
                       help="Mod key used in filenames")
    parser.add_argument("--test", action="store_true",
                       help="Generate test characters")
    parser.add_argument("--test-type", choices=["simple", "detailed", "extreme"], default="simple",
                       help="Type of test characters: simple/detailed/extreme")
    parser.add_argument("--config", type=str,
                       help="Path to JSON config with characters")
    parser.add_argument("--count", type=int, default=None,
                       help="Number of characters to generate (with --config)")
    
    args = parser.parse_args()
    
    generator = SCWImageGenerator(args.output_dir, args.modkey)
    
    # Check WebUI connection
    if not generator.check_webui_connection():
        print(f"Error: unable to connect to Stable Diffusion WebUI at {WEBUI_URL}")
        print("Ensure WebUI is running with --api flag")
        return
    
    print(f"Connected to WebUI: {WEBUI_URL}")
    
    characters = []
    
    if args.config:
        # Load characters from config
        characters = generator.load_characters_from_config(args.config)
        if args.count and args.count < len(characters):
            characters = characters[:args.count]
    elif args.test:
        # Load test characters of selected type
        print(f"🧪 Test mode: {args.test_type} characters")
        characters = generator.load_test_characters(args.test_type)
    else:
        print("Use one of the flags:")
        print("  --test                          - generate sample characters")
        print("  --config configs/character_config.json  - load characters from file")
        return
    
    if characters:
        print(f"Starting generation for {len(characters)} characters...")
        successful = 0
        
        for i, character in enumerate(characters, 1):
            print(f"\nGenerating character {i}/{len(characters)}")
            try:
                generated_files = generator.generate_character_images(character)
                if generated_files:
                    # Count total generated images
                    total_images = 0
                    for pose_files in generated_files.values():
                        if isinstance(pose_files, list):
                            total_images += len(pose_files)
                        else:
                            total_images += 1
                    
                    print(f"✓ Generated {total_images} images ({len(generated_files)} poses)")
                    successful += 1
                else:
                    print("✗ Failed to generate images")
            except KeyboardInterrupt:
                print("\nGeneration interrupted by user")
                break
            except Exception as e:
                print(f"✗ Character generation error: {e}")
                continue
        
        print(f"\nGeneration completed. Successfully created: {successful}/{len(characters)} characters")
    else:
        print("No characters to generate")

if __name__ == "__main__":
    main()
