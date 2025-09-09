#!/usr/bin/env python3
"""
Демонстрация новых возможностей SCW Image Generator

Показывает:
- Возрастная группа 0 (16+ лет)
- Маленькие размеры груди (s) 
- Очень большие размеры груди (x)
"""

from scw_image_generator import SCWImageGenerator, CharacterAttributes

def demo_new_features():
    """Демонстрирует новые функции генератора"""
    
    print("🎯 ДЕМО: Новые возможности SCW Image Generator")
    print("=" * 60)
    
    # Создаем генератор
    gen = SCWImageGenerator('demo_characters', 'demo')
    
    print(f"📁 Сессия демо: {gen.session_dir.name}")
    print()
    
    # 1. Очень молодая девушка с маленькой грудью
    print("👧 1. Очень молодая девушка (возраст 0) с маленькой грудью (s):")
    char1 = CharacterAttributes(
        gender='f', age_group=0, ethnicity='w',
        body_shape='s', breast_penis_size='s',
        hair_color='l', hair_length='l'
    )
    char_id1 = gen.generate_character_id(char1)
    filename1 = gen.generate_filename(char1, char_id1, 'head')
    prompt1 = gen.build_base_prompt(char1)
    
    print(f"   ID: {char_id1}")
    print(f"   Файл: {filename1}")
    print(f"   Промпт: {prompt1}")
    print()
    
    # 2. Зрелая женщина с очень большой грудью
    print("💃 2. Зрелая женщина (возраст 3) с очень большой грудью (x):")
    char2 = CharacterAttributes(
        gender='f', age_group=3, ethnicity='b',
        body_shape='c', breast_penis_size='x',
        hair_color='d', hair_length='m'
    )
    char_id2 = gen.generate_character_id(char2)
    filename2 = gen.generate_filename(char2, char_id2, 'head')
    prompt2 = gen.build_base_prompt(char2)
    
    print(f"   ID: {char_id2}")
    print(f"   Файл: {filename2}")
    print(f"   Промпт: {prompt2}")
    print()
    
    # 3. Молодой мужчина (для сравнения)
    print("🧔 3. Молодой мужчина (возраст 1) с мускулистым телом (l):")
    char3 = CharacterAttributes(
        gender='m', age_group=1, ethnicity='a',
        body_shape='f', breast_penis_size='l',
        hair_color='d', hair_length='s'
    )
    char_id3 = gen.generate_character_id(char3)
    filename3 = gen.generate_filename(char3, char_id3, 'head')
    prompt3 = gen.build_base_prompt(char3)
    
    print(f"   ID: {char_id3}")
    print(f"   Файл: {filename3}")
    print(f"   Промпт: {prompt3}")
    print()
    
    # Показываем новую систему размеров
    print("📏 Новая система размеров груди:")
    sizes = [
        ('s', 'Маленькая'),
        ('m', 'Средняя'),
        ('l', 'Большая'),
        ('h', 'Очень большая'),
        ('x', 'Экстра большая')
    ]
    
    for code, name in sizes:
        test_char = CharacterAttributes(gender='f', age_group=2, ethnicity='w', breast_penis_size=code)
        test_prompt = gen.build_base_prompt(test_char)
        breast_part = [part for part in test_prompt.split(', ') if 'breast' in part.lower()]
        breast_desc = breast_part[0] if breast_part else 'normal body'
        print(f"   {code}: {name:15} → {breast_desc}")
    
    print()
    
    # Показываем новую систему возрастов
    print("👥 Новая система возрастов:")
    ages = [
        (0, '16+ лет (подростки)'),
        (1, '18-24 лет'),
        (2, '22-31 лет'),
        (3, '28-42 лет'),
        (4, '38-51 лет'),
        (5, '48+ лет')
    ]
    
    for age_code, age_desc in ages:
        test_char = CharacterAttributes(gender='f', age_group=age_code, ethnicity='w')
        test_prompt = gen.build_base_prompt(test_char)
        age_part = [part for part in test_prompt.split(', ') if ('years old' in part or 'teen' in part)]
        age_prompt = age_part[0] if age_part else f'age group {age_code}'
        print(f"   {age_code}: {age_desc:20} → {age_prompt}")
    
    print()
    print("🎉 Демонстрация завершена!")
    print("📊 Используйте python scw_image_generator.py --config character_config.json")
    print("    для генерации с новыми пресетами персонажей!")

if __name__ == "__main__":
    demo_new_features()
