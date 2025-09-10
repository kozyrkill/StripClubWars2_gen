"""
Character configuration loading utilities
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .models import CharacterAttributes

class CharacterLoader:
    """Loads character configurations from various sources"""
    
    def __init__(self, configs_dir: str = "configs"):
        self.configs_dir = Path(configs_dir)
    
    def load_from_config(self, config_file: str) -> List[CharacterAttributes]:
        """Load characters from configuration file"""
        config_path = self._resolve_config_path(config_file)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            characters = []
            for char_data in data.get('character_presets', []):
                try:
                    character = CharacterAttributes.from_dict(char_data)
                    characters.append(character)
                except Exception as e:
                    print(f"⚠️ Error loading character {char_data.get('name', 'unknown')}: {e}")
            
            print(f"📋 Loaded {len(characters)} characters from {config_path}")
            return characters
            
        except FileNotFoundError:
            print(f"❌ Config file not found: {config_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {config_path}: {e}")
            return []
        except Exception as e:
            print(f"❌ Error loading config {config_path}: {e}")
            return []
    
    def load_test_characters(self, test_type: str = "simple") -> List[CharacterAttributes]:
        """Load test characters from test configuration"""
        test_config_path = self.configs_dir / "test_characters.json"
        
        try:
            with open(test_config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Select the desired character set
            if test_type == "simple":
                character_data = data.get("simple_characters", [])
            elif test_type == "diverse":
                character_data = data.get("diverse_characters", [])
            else:
                print(f"⚠️ Unknown test type: {test_type}")
                character_data = data.get("simple_characters", [])
            
            characters = []
            for char_data in character_data:
                try:
                    character = CharacterAttributes.from_dict(char_data)
                    characters.append(character)
                except Exception as e:
                    print(f"⚠️ Error loading test character: {e}")
                    
            return characters
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ {test_config_path} load error: {e}")
            print("Falling back to built-in sample characters")
            return self._create_sample_characters()
    
    def list_available_configs(self) -> List[str]:
        """List available configuration files"""
        if not self.configs_dir.exists():
            return []
        
        configs = []
        for config_file in self.configs_dir.glob("character_config*.json"):
            configs.append(config_file.name)
        
        return sorted(configs)
    
    def _resolve_config_path(self, config_file: str) -> Path:
        """Resolve configuration file path"""
        config_path = Path(config_file)
        
        # If it's already absolute, use as-is
        if config_path.is_absolute():
            return config_path
        
        # If it contains path separators, use as relative path
        if '/' in config_file or '\\' in config_file:
            return Path(config_file)
        
        # Otherwise, look in configs directory
        return self.configs_dir / config_file
    
    def _create_sample_characters(self) -> List[CharacterAttributes]:
        """Create built-in sample characters as fallback"""
        characters = [
            CharacterAttributes(
                name="sample_female_01",
                gender="f",
                age_group=2,
                ethnicity="w",
                height="m",
                body_shape="s",
                hips_size="s",
                breast_penis_size="s",
                skin_tone="l",
                hair_color="l",
                hair_length="l",
                eye_color="m"
            ),
            CharacterAttributes(
                name="sample_female_02", 
                gender="f",
                age_group=1,
                ethnicity="h",
                height="m",
                body_shape="n",
                hips_size="m",
                breast_penis_size="m",
                skin_tone="m",
                hair_color="m",
                hair_length="m",
                eye_color="m"
            ),
            CharacterAttributes(
                name="sample_male_01",
                gender="m",
                age_group=2,
                ethnicity="r",
                height="t",
                body_shape="f",
                hips_size="m",
                breast_penis_size="m",
                skin_tone="m",
                hair_color="d",
                hair_length="s",
                eye_color="d"
            )
        ]
        
        return characters
