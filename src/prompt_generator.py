"""
Prompt generation for Stable Diffusion
"""
from typing import Optional, Dict, Any
from .models import CharacterAttributes, PoseVariant
from .config import Config, PromptTemplates, PoseConfig

class PromptGenerator:
    """Generates prompts for Stable Diffusion"""
    
    def __init__(self):
        self.config = Config()
        self.templates = PromptTemplates()
        self.pose_config = PoseConfig()
    
    def build_base_prompt(self, character: CharacterAttributes) -> str:
        """Build base character prompt"""
        parts = [
            self.config.BASE_PROMPT_QUALITY,
            self.templates.GENDER_PROMPTS.get(character.gender, "person"),
            self.templates.AGE_PROMPTS.get(character.age_group, "adult"),
            self.templates.ETHNICITY_PROMPTS.get(character.ethnicity, ""),
            self.templates.BODY_SHAPE_PROMPTS.get(character.body_shape, "normal build"),
            self.templates.HAIR_COLOR_PROMPTS.get(character.hair_color, "brown hair"),
            self.templates.HAIR_LENGTH_PROMPTS.get(character.hair_length, "medium hair"),
            "natural hair",
            f"{character.expression} expression"
        ]
        
        # Add breast/body size descriptions
        if character.gender == "f":
            breast_desc = self._get_breast_description(character.breast_penis_size)
            if breast_desc:
                parts.append(breast_desc)
        else:
            body_desc = self._get_male_body_description(character.breast_penis_size)
            if body_desc:
                parts.append(body_desc)
        
        return ", ".join(filter(None, parts))
    
    def build_pose_prompt(self, base_prompt: str, pose: str, reveal_level: int = 0, 
                         variant_idx: int = 0, gender: Optional[str] = None) -> str:
        """Build complete prompt for specific pose"""
        # Handle pose aliases
        effective_pose = self.pose_config.POSE_ALIAS_MAP.get(pose, pose)
        
        # Start with full body emphasis for non-headshots
        prompt_parts = []
        if effective_pose != "head":
            prompt_parts.append(self.templates.FULL_BODY_PROMPT)
        
        prompt_parts.extend([
            base_prompt,
            self.pose_config.POSE_PROMPTS.get(effective_pose, "standing pose, complete figure")
        ])
        
        # Add clothing description
        clothing_desc = self.get_clothing_description(effective_pose, reveal_level, gender)
        if clothing_desc:
            prompt_parts.append(clothing_desc)
        
        # Add pose diversification for variety
        pose_variety = self._get_pose_diversification(effective_pose, variant_idx)
        if pose_variety:
            prompt_parts.append(pose_variety)
        
        prompt_parts.append(self.config.STYLE_PROMPT)
        
        return ", ".join(filter(None, prompt_parts))
    
    def generate_negative_prompt(self, pose: Optional[str] = None, gender: Optional[str] = None) -> str:
        """Generate negative prompt"""
        negative_parts = [self.config.BASE_NEGATIVE_PROMPT]
        
        # Add gender-specific negatives
        if gender == "m":
            negative_parts.append("vulva, labia, clitoris, vagina, breasts, boobs")
        elif gender == "f":
            negative_parts.append("penis, testicles, scrotum, male genitalia")
        
        # Add pose-specific negatives for nude/semi-nude
        if pose and pose in ["nude", "tl", "uw", "ss", "s1", "s2", "s3"]:
            negative_parts.append(self.templates.ANTI_CROPPING_NEGATIVES)
        
        return " ".join(negative_parts)
    
    def get_clothing_description(self, pose: str, reveal_level: int, gender: Optional[str] = None) -> str:
        """Get clothing description for pose and reveal level"""
        clothing_map = self._get_clothing_map(gender or "f")
        
        pose_clothing = clothing_map.get(pose, {})
        clothing_desc = pose_clothing.get(reveal_level, "appropriate clothing")
        
        # Add footwear
        footwear = self._get_footwear_description(pose, reveal_level, gender)
        if footwear and footwear not in clothing_desc:
            clothing_desc += f", {footwear}"
        
        return clothing_desc
    
    def _get_breast_description(self, size: str) -> str:
        """Get breast size description for females"""
        size_map = {
            "s": "small breasts, tiny chest, petite bust",
            "m": "medium breasts, average chest",
            "l": "large breasts, big chest, full bust",
            "h": "huge breasts, very large chest, massive bust",
            "x": "extra huge breasts, gigantic bust, massive boobs"
        }
        return size_map.get(size, "medium breasts")
    
    def _get_male_body_description(self, size: str) -> str:
        """Get body description for males"""
        size_map = {
            "s": "lean build, slim",
            "m": "average build",
            "l": "athletic build, muscular",
            "h": "muscular build, strong",
            "x": "very muscular, bodybuilder"
        }
        return size_map.get(size, "average build")
    
    def _get_pose_diversification(self, pose: str, variant_idx: int) -> str:
        """Get pose variety descriptors"""
        diversification_map = {
            "nude": [
                "natural stance, relaxed arms, subtle smile, legs apart, shoulder-width stance",
                "arms on hips, confident posture, looking at viewer, front view pelvis visible, legs apart",
                "one hand behind head, playful smile, slight hip tilt, pelvis unobstructed, legs apart"
            ],
            "cas": [
                "standing straight, hands at sides",
                "one leg forward, casual stance", 
                "hands in pockets, relaxed"
            ],
            "tl": [
                "arms crossed under chest, subtle smile, topless emphasized, exposed breasts",
                "one arm behind head, other on hip, playful, bare chest visible, exposed breasts",
                "hands on hips, confident, looking at viewer, no top, no bra, exposed breasts"
            ]
        }
        
        variations = diversification_map.get(pose, [""])
        if variations and variant_idx < len(variations):
            return variations[variant_idx]
        return ""
    
    def _get_footwear_description(self, pose: str, reveal_level: int, gender: Optional[str] = None) -> str:
        """Get footwear description"""
        footwear_map = {
            "cas": {0: "white sneakers, cotton socks", 1: "stylish sneakers, ankle socks", 2: "fashionable boots, bare legs"},
            "bc": {0: "black office shoes, nude pantyhose", 1: "high heels, sheer stockings", 2: "stiletto heels, lace-top stockings"},
            "biz": {0: "conservative black pumps, professional pantyhose", 1: "elegant heels, nude stockings", 2: "sexy high heels, seductive stockings"},
            "uw": {3: "bare feet, no socks", 4: "thigh-high stockings, bare feet", 5: "sexy stockings with garters, bare feet"},
            "ss": {2: "bare feet, swimming attire", 3: "beach sandals or bare feet", 4: "bare feet, minimal swimwear"},
            "fun": {0: "athletic shoes, sports socks", 1: "running shoes, ankle socks", 2: "gym shoes, athletic wear"},
            "tl": {6: "high heels", 7: "stiletto heels", 8: "platform heels"},
            "nude": {9: "bare feet", 10: "bare feet", 11: "bare feet"}
        }
        
        return footwear_map.get(pose, {}).get(reveal_level, "appropriate shoes")
    
    def _get_clothing_map(self, gender: str) -> Dict[str, Dict[int, str]]:
        """Get clothing descriptions by gender"""
        if gender == "f":
            return {
                "cas": {
                    0: "blue jeans and white t-shirt, casual everyday outfit",
                    1: "fitted dark jeans and tight colorful top, stylish casual", 
                    2: "short denim skirt and crop top, trendy casual showing some skin"
                },
                "bc": {
                    0: "white business blouse and dark pants, conservative professional attire",
                    1: "fitted gray blazer and pencil skirt, professional but elegant",
                    2: "partially unbuttoned blouse and tight skirt, business casual revealing"
                },
                "biz": {
                    0: "dark business suit with jacket and pants, formal conservative wear",
                    1: "fitted navy suit with short skirt, professional attractive look",
                    2: "open suit jacket with tight blouse and mini skirt, formal revealing"
                },
                "uw": {
                    3: "matching white cotton bra and panties, classic lingerie set",
                    4: "black lacy bra and panties, elegant semi-transparent underwear, sheer mesh panels",
                    5: "red silk lingerie set, barely covering, seductive underwear, see-through mesh, semi-transparent"
                },
                "ss": {
                    2: "blue one-piece swimsuit, modest athletic swimming attire",
                    3: "colorful bikini top and bottom, classic two-piece beachwear, sheer mesh panels",
                    4: "tiny string bikini, minimal coverage, revealing swimwear, semi-transparent elements"
                },
                "tl": {
                    6: "topless, panties only (thong or g-string), no top, exposed breasts",
                    7: "topless, micro skirt or shorts with exposed breasts, no bra",
                    8: "topless, sheer lace panties or mesh bottoms, exposed breasts, no bra"
                },
                "s1": {
                    1: "sparkly sequined mini dress, fishnet stockings, sheer mesh panels",
                    2: "tight mini dress with deep neckline, thigh-high stockings, garter belt, semi-transparent", 
                    3: "corset top with short skirt, fishnets, feather boa, rhinestones, see-through details"
                },
                "s2": {
                    3: "black corset and g-string, garter belt, fishnet stockings, gloves, sheer mesh",
                    4: "latex mini dress, thigh-high stockings, platform heels, choker, semi-transparent sections",
                    5: "pasties and g-string, garter belt, fishnets, feather boa, glitter, see-through elements"
                },
                "s3": {
                    5: "micro bikini top and thong, fishnets, garter belt, high heels, glitter, transparent mesh",
                    6: "strappy lingerie harness, g-string, thigh-highs, platform heels, rhinestones, see-through",
                    7: "nipple pasties, g-string, body glitter, feather boa, high heels, semi-transparent mesh"
                },
                "nude": {
                    9: "no clothing, fully nude, bare skin, no outfit, no lingerie, hairless pubic area",
                    10: "no clothing, fully nude, bare skin, no outfit, no lingerie, hairless pubic area", 
                    11: "no clothing, fully nude, bare skin, no outfit, no lingerie, hairless pubic area"
                }
            }
        else:  # male
            return {
                "cas": {
                    0: "jeans and t-shirt, casual outfit",
                    1: "fitted t-shirt and jeans, casual wear",
                    2: "shorts and tank top, casual sportswear"
                },
                "bc": {
                    0: "button-up shirt and slacks, conservative professional",
                    1: "fitted shirt and slacks, business casual"
                },
                "biz": {
                    0: "business suit with tie, formal wear",
                    1: "fitted suit, no tie, professional"
                },
                "uw": {
                    3: "boxers",
                    4: "briefs", 
                    5: "boxer briefs"
                },
                "nude": {
                    9: "no clothing, fully nude, bare skin, no outfit, no lingerie, hairless pubic area",
                    10: "no clothing, fully nude, bare skin, no outfit, no lingerie, hairless pubic area",
                    11: "no clothing, fully nude, bare skin, no outfit, no lingerie, hairless pubic area"
                }
            }
