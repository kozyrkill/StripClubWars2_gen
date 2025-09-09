#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCW Character Image Pack Generator
Генератор имедж-паков для игры Strip Club Wars 2

Использует Stable Diffusion WebUI API для генерации изображений персонажей
с последующей обработкой в соответствии с требованиями игры.
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

# Конфигурация Stable Diffusion WebUI
WEBUI_URL = "http://localhost:7860"
WEBUI_API_URL = f"{WEBUI_URL}/sdapi/v1"

@dataclass
class CharacterAttributes:
    """Атрибуты персонажа для генерации"""
    # Обязательные атрибуты (reqphys)
    gender: str  # m/f
    age_group: int  # 1-5 (18-24, 22-31, 28-42, 38-51, 48+)
    ethnicity: str  # w/b/h/a/r (white, black, hispanic, asian, middle-eastern)
    
    # Опциональные атрибуты (optphys)
    height: str = "m"  # t/m/s (tall, medium, short)
    body_shape: str = "n"  # s/n/c/f (slim, normal, curvy, fit)
    hips_size: str = "m"  # s/m/l (small, medium, large)
    breast_penis_size: str = "m"  # s/m/l/h (small, medium, large, huge)
    skin_tone: str = "l"  # l/m/d (light, medium, dark)
    
    # Атрибуты изображения (imgphys)
    hair_color: str = "m"  # l/m/d (light, medium, dark)
    hair_length: str = "m"  # b/s/m/l (bald, short, medium, long)
    eye_color: str = "m"  # l/m/d (light, medium, dark)

# Конфигурация поз и их откровенности (с поддержкой множественных вариантов)
POSES_CONFIG = {
    # Базовые позы для всех персонажей
    "head": {"reveal_variants": [0], "required": True, "description": "headshot"},
    "cas": {"reveal_variants": [0, 1, 2], "required": True, "description": "casual clothes"},
    "uw": {"reveal_variants": [3, 4, 5], "required": True, "description": "underwear"},
    "nude": {"reveal_variants": [9, 10, 11], "required": True, "description": "nude"},
    
    # Дополнительные позы
    "bc": {"reveal_variants": [0, 1], "required": False, "description": "business casual"},
    "biz": {"reveal_variants": [0, 1], "required": False, "description": "business suit"},
    "fun": {"reveal_variants": [0, 1, 2], "required": False, "description": "fun/workout clothes"},
    
    # Только для женщин
    "tl": {"reveal_variants": [6, 7, 8], "required": False, "description": "topless", "female_only": True},
    "ss": {"reveal_variants": [2, 3, 4], "required": False, "description": "swimsuit", "female_only": True},
    "s1": {"reveal_variants": [1, 2, 3], "required": False, "description": "stripper outfit 1", "female_only": True},
    "s2": {"reveal_variants": [3, 4, 5], "required": False, "description": "stripper outfit 2", "female_only": True},
    "s3": {"reveal_variants": [5, 6, 7], "required": False, "description": "stripper outfit 3", "female_only": True},
    "preg": {"reveal_variants": [1, 3, 6], "required": False, "description": "pregnant", "female_only": True},
}

# Словари для перевода атрибутов в промпты
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
    "head": "portrait, headshot, face focus, upper body",
    "cas": "casual clothes, jeans, t-shirt, everyday wear",
    "bc": "business casual, nice shirt, slacks, professional but relaxed",
    "biz": "business suit, formal wear, professional attire",
    "fun": "workout clothes, gym wear, athletic clothing, shorts, sports bra",
    "uw": "underwear, lingerie, panties and bra, boxers, briefs",
    "ss": "swimsuit, bikini, swimming attire",
    "tl": "topless, bare chest, no shirt, nude from waist up",
    "nude": "nude, naked, no clothes, full body nude",
    "s1": "sexy outfit, revealing dress, club wear",
    "s2": "very revealing outfit, stripper costume, barely covered",
    "s3": "extremely revealing, almost nude, tiny outfit",
    "preg": "pregnant belly, maternity clothes, expecting"
}

class SCWImageGenerator:
    """Генератор изображений для SCW"""
    
    def __init__(self, output_dir: str = "generated_characters", modkey: str = "custom"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.modkey = modkey
        self.current_id = 1000  # Начинаем с ID 1000 для пользовательских персонажей
        
    def check_webui_connection(self) -> bool:
        """Проверяет соединение с Stable Diffusion WebUI"""
        try:
            response = requests.get(f"{WEBUI_API_URL}/options")
            return response.status_code == 200
        except:
            return False
    
    def generate_character_id(self, character: CharacterAttributes) -> str:
        """Генерирует уникальный ID для персонажа"""
        if character.gender == "f":
            # Женщины начинаются с 0
            char_id = f"{self.current_id:05d}"
        else:
            # Мужчины начинаются с 1
            char_id = f"{10000 + self.current_id:05d}"
        
        self.current_id += 1
        return char_id
    
    def build_base_prompt(self, character: CharacterAttributes) -> str:
        """Создает базовый промпт для персонажа"""
        prompt_parts = []
        
        # Основные характеристики
        prompt_parts.append(GENDER_PROMPTS[character.gender])
        prompt_parts.append(AGE_PROMPTS[character.age_group])
        prompt_parts.append(ETHNICITY_PROMPTS[character.ethnicity])
        
        # Телосложение
        prompt_parts.append(BODY_SHAPE_PROMPTS[character.body_shape])
        
        # Волосы
        prompt_parts.append(HAIR_COLOR_PROMPTS[character.hair_color])
        prompt_parts.append(HAIR_LENGTH_PROMPTS[character.hair_length])
        
        # Дополнительные характеристики
        if character.breast_penis_size == "l":
            if character.gender == "f":
                prompt_parts.append("large breasts")
            else:
                prompt_parts.append("athletic build")
        elif character.breast_penis_size == "h":
            if character.gender == "f":
                prompt_parts.append("huge breasts, very large bust")
        
        return ", ".join(prompt_parts)
    
    def build_pose_prompt(self, base_prompt: str, pose: str, reveal_level: int = 0) -> str:
        """Создает промпт для конкретной позы с учетом уровня откровенности"""
        pose_prompt = POSE_PROMPTS.get(pose, "")
        
        # Модификация промпта в зависимости от уровня откровенности
        reveal_modifiers = {
            0: "modest, conservative, fully clothed",
            1: "slightly revealing, tasteful",
            2: "moderately revealing, stylish", 
            3: "revealing, sexy",
            4: "very revealing, provocative",
            5: "highly revealing, seductive",
            6: "extremely revealing, erotic",
            7: "barely covered, explicit",
            8: "almost nude, very explicit",
            9: "nude, artistic nudity",
            10: "nude, sensual",
            11: "nude, very explicit"
        }
        
        reveal_modifier = reveal_modifiers.get(reveal_level, "")
        
        # Базовые настройки качества
        quality_prompt = "masterpiece, best quality, high resolution, detailed, realistic, photorealistic"
        
        # Настройки освещения и стиля
        style_prompt = "soft lighting, professional photography, clean background"
        
        # Компонуем итоговый промпт
        full_prompt = f"{quality_prompt}, {base_prompt}, {pose_prompt}, {reveal_modifier}, {style_prompt}"
        
        return full_prompt
    
    def generate_negative_prompt(self) -> str:
        """Создает негативный промпт"""
        return ("low quality, blurry, distorted, deformed, ugly, bad anatomy, "
                "extra limbs, missing limbs, watermark, signature, text, "
                "bad hands, malformed hands, extra fingers, missing fingers")
    
    def call_stable_diffusion_api(self, prompt: str, is_headshot: bool = False) -> Optional[Image.Image]:
        """Вызывает API Stable Diffusion WebUI для генерации изображения"""
        
        # Размеры изображения
        width = 120 if is_headshot else 512
        height = 160 if is_headshot else 800
        
        payload = {
            "prompt": prompt,
            "negative_prompt": self.generate_negative_prompt(),
            "width": width,
            "height": height,
            "steps": 30,
            "cfg_scale": 7.5,
            "sampler_name": "DPM++ 2M Karras",
            "batch_size": 1,
            "n_iter": 1,
            "seed": -1,
            "restore_faces": True,
        }
        
        try:
            response = requests.post(f"{WEBUI_API_URL}/txt2img", json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("images"):
                    # Декодируем base64 изображение
                    image_data = base64.b64decode(result["images"][0])
                    return Image.open(io.BytesIO(image_data))
            return None
        except Exception as e:
            print(f"Ошибка генерации изображения: {e}")
            return None
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Удаляет фон с изображения"""
        try:
            # Конвертируем в RGB если нужно
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Удаляем фон с помощью rembg
            output = remove(image)
            return output
        except Exception as e:
            print(f"Ошибка удаления фона: {e}")
            # Возвращаем оригинальное изображение в случае ошибки
            return image
    
    def generate_filename(self, character: CharacterAttributes, char_id: str, pose: str, reveal_level: int = 0) -> str:
        """Генерирует имя файла в соответствии с форматом SCW"""
        
        if pose == "head":
            # Формат для головы: modkey-id-reqphys-optphys-imgphys-special-head.png
            reqphys = f"{character.gender}{character.age_group}{character.ethnicity}"
            optphys = f"{character.height}{character.body_shape}{character.hips_size}{character.breast_penis_size}{character.skin_tone}"
            imgphys = f"{character.hair_color}{character.hair_length}{character.eye_color}"
            special = "u"  # обычный персонаж
            
            filename = f"{self.modkey}-{char_id}-{reqphys}-{optphys}-{imgphys}-{special}-head.png"
        else:
            # Формат для остальных поз: modkey-id-reveal-pose.png
            filename = f"{self.modkey}-{char_id}-z{reveal_level}-{pose}.png"
        
        return filename
    
    def generate_character_images(self, character: CharacterAttributes, poses: List[str] = None) -> Dict[str, str]:
        """Генерирует все изображения для персонажа с множественными вариантами"""
        
        if poses is None:
            # Генерируем все обязательные позы
            poses = [pose for pose, config in POSES_CONFIG.items() 
                    if config.get("required", False)]
            
            # Добавляем женские позы если персонаж женского пола
            if character.gender == "f":
                female_poses = [pose for pose, config in POSES_CONFIG.items() 
                              if config.get("female_only", False)]
                poses.extend(female_poses[:3])  # Добавляем первые 3 женские позы
        
        char_id = self.generate_character_id(character)
        base_prompt = self.build_base_prompt(character)
        
        print(f"Генерирую персонажа {char_id} ({character.gender}, {character.age_group}, {character.ethnicity})")
        
        generated_files = {}
        
        for pose in poses:
            # Пропускаем женские позы для мужских персонажей
            if POSES_CONFIG[pose].get("female_only", False) and character.gender == "m":
                continue
                
            print(f"  Генерирую позу: {pose}")
            
            # Получаем варианты уровней откровенности для этой позы
            reveal_variants = POSES_CONFIG[pose].get("reveal_variants", [0])
            pose_files = []
            
            for variant_idx, reveal_level in enumerate(reveal_variants):
                print(f"    Вариант {variant_idx + 1}/3 (уровень откровенности: {reveal_level})")
                
                # Создаем промпт для позы с учетом уровня откровенности
                full_prompt = self.build_pose_prompt(base_prompt, pose, reveal_level)
                
                # Генерируем изображение
                is_headshot = pose == "head"
                image = self.call_stable_diffusion_api(full_prompt, is_headshot)
                
                if image:
                    # Удаляем фон (кроме головы, для неё это менее критично)
                    if not is_headshot:
                        image = self.remove_background(image)
                    
                    # Генерируем имя файла с учетом уровня откровенности
                    filename = self.generate_filename(character, char_id, pose, reveal_level)
                    filepath = self.output_dir / filename
                    
                    # Сохраняем изображение
                    image.save(filepath, "PNG")
                    pose_files.append(str(filepath))
                    
                    print(f"      Сохранено: {filename}")
                    
                    # Небольшая пауза между генерациями
                    time.sleep(1)
                else:
                    print(f"      Ошибка генерации варианта {variant_idx + 1}")
            
            if pose_files:
                generated_files[pose] = pose_files
                print(f"    Создано {len(pose_files)} вариантов позы {pose}")
            else:
                print(f"    ❌ Не удалось создать ни одного варианта позы {pose}")
        
        return generated_files

    def load_characters_from_config(self, config_file: str) -> List[CharacterAttributes]:
        """Загружает персонажей из JSON конфигурации"""
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
            print(f"Ошибка загрузки конфигурации: {e}")
            return self.create_sample_characters()
            
        return characters
    
    def create_sample_characters(self) -> List[CharacterAttributes]:
        """Создает примеры персонажей для тестирования"""
        characters = []
        
        # Молодая кавказская женщина
        characters.append(CharacterAttributes(
            gender="f", age_group=2, ethnicity="w",
            body_shape="n", breast_penis_size="m",
            hair_color="l", hair_length="l", eye_color="m"
        ))
        
        # Зрелый азиатский мужчина
        characters.append(CharacterAttributes(
            gender="m", age_group=4, ethnicity="a",
            body_shape="f", breast_penis_size="m",
            hair_color="d", hair_length="s", eye_color="d"
        ))
        
        # Молодая афроамериканка
        characters.append(CharacterAttributes(
            gender="f", age_group=1, ethnicity="b",
            body_shape="c", breast_penis_size="l",
            hair_color="d", hair_length="m", eye_color="d"
        ))
        
        return characters

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="SCW Character Image Generator")
    parser.add_argument("--output-dir", default="generated_characters", 
                       help="Директория для сохранения изображений")
    parser.add_argument("--modkey", default="custom", 
                       help="Ключ мода для имен файлов")
    parser.add_argument("--test", action="store_true",
                       help="Генерировать тестовых персонажей")
    parser.add_argument("--config", type=str,
                       help="JSON файл с конфигурацией персонажей")
    parser.add_argument("--count", type=int, default=None,
                       help="Количество персонажей для генерации (для --config)")
    
    args = parser.parse_args()
    
    generator = SCWImageGenerator(args.output_dir, args.modkey)
    
    # Проверяем подключение к WebUI
    if not generator.check_webui_connection():
        print(f"Ошибка: не удается подключиться к Stable Diffusion WebUI на {WEBUI_URL}")
        print("Убедитесь что WebUI запущен с флагом --api")
        return
    
    print(f"Подключение к WebUI успешно: {WEBUI_URL}")
    
    characters = []
    
    if args.config:
        # Загружаем персонажей из конфигурации
        characters = generator.load_characters_from_config(args.config)
        if args.count and args.count < len(characters):
            characters = characters[:args.count]
    elif args.test:
        # Генерируем тестовых персонажей
        characters = generator.create_sample_characters()
    else:
        print("Используйте один из флагов:")
        print("  --test                    - генерировать примеры персонажей")
        print("  --config character_config.json - загрузить персонажей из файла")
        return
    
    if characters:
        print(f"Начинаю генерацию {len(characters)} персонажей...")
        successful = 0
        
        for i, character in enumerate(characters, 1):
            print(f"\nГенерирую персонажа {i}/{len(characters)}")
            try:
                generated_files = generator.generate_character_images(character)
                if generated_files:
                    # Подсчитываем общее количество сгенерированных изображений
                    total_images = 0
                    for pose_files in generated_files.values():
                        if isinstance(pose_files, list):
                            total_images += len(pose_files)
                        else:
                            total_images += 1
                    
                    print(f"✓ Сгенерировано {total_images} изображений ({len(generated_files)} поз)")
                    successful += 1
                else:
                    print("✗ Не удалось сгенерировать изображения")
            except KeyboardInterrupt:
                print("\nГенерация прервана пользователем")
                break
            except Exception as e:
                print(f"✗ Ошибка генерации персонажа: {e}")
                continue
        
        print(f"\nГенерация завершена. Успешно создано: {successful}/{len(characters)} персонажей")
    else:
        print("Нет персонажей для генерации")

if __name__ == "__main__":
    main()
