"""
Main character image generator
"""
import os
import json
import hashlib
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from .models import CharacterAttributes, GenerationSettings, GenerationResult
from .config import Config, PoseConfig
from .prompt_generator import PromptGenerator
from .sd_client import StableDiffusionClient
from .image_processor import ImageProcessor

class CharacterImageGenerator:
    """Main character image generator class"""
    
    def __init__(self, output_dir: str = None, modkey: str = None):
        self.config = Config()
        self.pose_config = PoseConfig()
        self.modkey = modkey or self.config.DEFAULT_MODKEY
        self.output_dir = output_dir or self.config.DEFAULT_OUTPUT_DIR
        
        # Initialize components
        self.prompt_generator = PromptGenerator()
        self.sd_client = StableDiffusionClient(self.config)
        self.image_processor = ImageProcessor(self.config)
        
        # Create session directory
        self.session_dir = self._create_session_directory()
        
        print(f"📁 Session: {self.session_dir.name}")
    
    def check_webui_connection(self) -> bool:
        """Check WebUI connection"""
        if self.sd_client.check_connection():
            print(f"Connected to WebUI: {self.config.WEBUI_URL}")
            return True
        else:
            print(f"❌ Cannot connect to WebUI at {self.config.WEBUI_URL}")
            print("Make sure Stable Diffusion WebUI is running with --api flag")
            return False
    
    def generate_character_images(self, character: CharacterAttributes, 
                                poses: List[str] = None) -> Dict[str, List[GenerationResult]]:
        """Generate all images for a character"""
        char_id = self._generate_character_id(character)
        char_seed = self._generate_character_seed(char_id)
        base_prompt = self.prompt_generator.build_base_prompt(character)
        
        print(f"Generating character {char_id} (seed: {char_seed})")
        print(f"  Attributes: gender={character.gender}, age_group={character.age_group}, ethnicity={character.ethnicity}")
        print(f"  Variety via clothing per reveal level")
        
        # Use provided poses or get default poses
        if poses is None:
            poses = self._get_default_poses(character.gender)
        
        results = {}
        total_images = 0
        
        for pose in poses:
            print(f"  Pose: {pose}")
            pose_results = self._generate_pose_variants(
                character, char_id, char_seed, base_prompt, pose
            )
            results[pose] = pose_results
            successful_results = [r for r in pose_results if r.success]
            total_images += len(successful_results)
            print(f"    ✅ Created {len(successful_results)} variants for pose {pose}")
        
        print(f"✓ Generated {total_images} images ({len(poses)} poses)")
        return results
    
    def load_characters_from_config(self, config_file: str) -> List[CharacterAttributes]:
        """Load characters from configuration file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            characters = []
            for char_data in data.get('character_presets', []):
                try:
                    character = CharacterAttributes.from_dict(char_data)
                    characters.append(character)
                except Exception as e:
                    print(f"⚠️ Error loading character {char_data.get('name', 'unknown')}: {e}")
            
            print(f"📋 Loaded {len(characters)} characters from {config_file}")
            return characters
            
        except Exception as e:
            print(f"❌ Error loading config {config_file}: {e}")
            return []
    
    def _create_session_directory(self) -> Path:
        """Create session directory for this generation run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = f"{self.modkey}_{timestamp}"
        session_path = Path(self.output_dir) / session_name
        session_path.mkdir(parents=True, exist_ok=True)
        return session_path
    
    def _generate_character_id(self, character: CharacterAttributes) -> str:
        """Generate unique character ID"""
        # Create timestamp-based random ID
        timestamp = int(time.time() * 1000) % 100000  # Last 5 digits of timestamp
        random_part = random.randint(0, 9999)
        
        if character.gender == "f":
            # Female IDs: 0-49999
            char_id = (timestamp + random_part) % 50000
        else:
            # Male IDs: 10000-19999  
            char_id = 10000 + ((timestamp + random_part) % 10000)
            
        return f"{char_id:05d}"
    
    def _generate_character_seed(self, char_id: str) -> int:
        """Generate consistent seed for character"""
        seed_string = f"{self.modkey}-{char_id}"
        hash_object = hashlib.md5(seed_string.encode())
        return int(hash_object.hexdigest()[:8], 16)
    
    def _get_default_poses(self, gender: str) -> List[str]:
        """Get default poses for gender"""
        poses = ["head", "cas", "uw", "nude", "bc", "fun"]
        
        if gender == "f":
            poses.extend(["tl", "ss", "s1"])
        
        return poses
    
    def _generate_pose_variants(self, character: CharacterAttributes, char_id: str, 
                               char_seed: int, base_prompt: str, pose: str) -> List[GenerationResult]:
        """Generate all variants for a pose"""
        effective_pose = self.pose_config.POSE_ALIAS_MAP.get(pose, pose)
        pose_config = self.pose_config.POSES_CONFIG.get(effective_pose, {})
        reveal_variants = pose_config.get("reveal_variants", [0])
        
        results = []
        
        for i, reveal_level in enumerate(reveal_variants):
            variant_idx = i + 1
            print(f"    Variant {variant_idx}/{len(reveal_variants)} (reveal level: {reveal_level})")
            
            # Generate clothing description
            clothing_desc = self.prompt_generator.get_clothing_description(
                effective_pose, reveal_level, character.gender
            )
            print(f"      Clothing: {clothing_desc}")
            
            # Build prompts
            full_prompt = self.prompt_generator.build_pose_prompt(
                base_prompt, effective_pose, reveal_level, i, character.gender
            )
            negative_prompt = self.prompt_generator.generate_negative_prompt(
                effective_pose, character.gender
            )
            
            # Print prompts for debugging
            print(f"      📝 FULL PROMPT:")
            print(f"         {full_prompt}")
            print(f"      📝 NEGATIVE PROMPT:")
            print(f"         {negative_prompt}")
            
            # Generate image
            result = self._generate_single_image(
                character, char_id, char_seed, effective_pose, reveal_level,
                full_prompt, negative_prompt, clothing_desc
            )
            
            results.append(result)
            
            if result.success:
                print(f"      Saved: {result.filename}")
            else:
                print(f"      ❌ Failed: {result.error}")
            
            # Delay between generations
            if self.config.DELAY_BETWEEN_GENERATIONS > 0:
                time.sleep(self.config.DELAY_BETWEEN_GENERATIONS)
        
        return results
    
    def _generate_single_image(self, character: CharacterAttributes, char_id: str, 
                              char_seed: int, pose: str, reveal_level: int,
                              prompt: str, negative_prompt: str, 
                              clothing_desc: str) -> GenerationResult:
        """Generate a single image"""
        try:
            # Determine image settings
            is_headshot = (pose == "head")
            if is_headshot:
                settings = GenerationSettings(
                    steps=self.config.HEADSHOT_STEPS,
                    cfg_scale=self.config.HEADSHOT_CFG_SCALE,
                    sampler=self.config.DEFAULT_SAMPLER,
                    seed=char_seed,
                    width=self.config.HEAD_GENERATION_SIZE[0],
                    height=self.config.HEAD_GENERATION_SIZE[1]
                )
            else:
                settings = GenerationSettings(
                    steps=self.config.DEFAULT_STEPS,
                    cfg_scale=self.config.DEFAULT_CFG_SCALE,
                    sampler=self.config.DEFAULT_SAMPLER,
                    seed=char_seed,
                    width=self.config.BODY_GENERATION_SIZE[0],
                    height=self.config.BODY_GENERATION_SIZE[1]
                )
            
            # Generate image
            image = self.sd_client.generate_image(prompt, negative_prompt, settings)
            if image is None:
                return GenerationResult(
                    success=False,
                    error="Failed to generate image",
                    pose=pose,
                    reveal_level=reveal_level
                )
            
            # Process image
            if is_headshot:
                processed_image = self.image_processor.process_headshot(image)
            else:
                processed_image = self.image_processor.process_body_image(image)
            
            # Generate filename
            filename = self._generate_filename(character, char_id, pose, reveal_level)
            filepath = self.session_dir / filename
            
            # Save image
            processed_image.save(filepath, "PNG", optimize=True)
            
            return GenerationResult(
                success=True,
                filename=filename,
                pose=pose,
                reveal_level=reveal_level
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e),
                pose=pose,
                reveal_level=reveal_level
            )
    
    def _generate_filename(self, character: CharacterAttributes, char_id: str, 
                          pose: str, reveal_level: int) -> str:
        """Generate filename following SCW naming convention"""
        if pose == "head":
            # Headshot filename: modkey-id-reqphys-optphys-imgphys-special-head.png
            reqphys = f"{character.gender}{character.age_group}{character.ethnicity}"
            optphys = f"{character.height}{character.body_shape}{character.hips_size}{character.breast_penis_size}{character.skin_tone}"
            imgphys = f"{character.hair_color}{character.hair_length}{character.eye_color}"
            special = "u"  # Default special code
            
            return f"{self.modkey}-{char_id}-{reqphys}-{optphys}-{imgphys}-{special}-head.png"
        else:
            # Body filename: modkey-id-z<reveal>-pose.png
            return f"{self.modkey}-{char_id}-z{reveal_level}-{pose}.png"
