"""
Data models for SCW Character Image Generator
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

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
    
    # Additional attributes for variety
    hair_style: str = "natural"
    facial_hair: str = "none"
    makeup: str = "natural"
    tattoos: str = "none"
    piercings: str = "none"
    expression: str = "neutral"
    clothing_style: str = "casual"
    
    # Character name for identification
    name: str = "unnamed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'gender': self.gender,
            'age_group': self.age_group,
            'ethnicity': self.ethnicity,
            'height': self.height,
            'body_shape': self.body_shape,
            'hips_size': self.hips_size,
            'breast_penis_size': self.breast_penis_size,
            'skin_tone': self.skin_tone,
            'hair_color': self.hair_color,
            'hair_length': self.hair_length,
            'eye_color': self.eye_color,
            'hair_style': self.hair_style,
            'facial_hair': self.facial_hair,
            'makeup': self.makeup,
            'tattoos': self.tattoos,
            'piercings': self.piercings,
            'expression': self.expression,
            'clothing_style': self.clothing_style
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterAttributes':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class GenerationSettings:
    """Settings for image generation"""
    steps: int = 30
    cfg_scale: float = 12.0
    sampler: str = "DPM++ 2M Karras"
    seed: int = -1
    width: int = 512
    height: int = 800
    
@dataclass
class PoseVariant:
    """Information about a pose variant"""
    pose: str
    reveal_level: int
    variant_index: int
    clothing_description: str
    prompt: str
    negative_prompt: str

@dataclass
class GenerationResult:
    """Result of image generation"""
    success: bool
    filename: Optional[str] = None
    error: Optional[str] = None
    pose: Optional[str] = None
    reveal_level: Optional[int] = None
