#!/usr/bin/env python3
"""
Демонстрация постоянного seed и детализированных персонажей

Показывает:
- Постоянный seed для консистентных изображений персонажа
- Детализированные атрибуты (татуировки, макияж, стиль волос и т.д.)
- Различные наборы тестовых персонажей
"""

from scw_image_generator import SCWImageGenerator, CharacterAttributes
from test_characters import get_detailed_test_characters, get_simple_test_characters, get_extreme_test_characters

def demo_seed_consistency():
    """Демонстрирует работу постоянного seed"""
    
    print("🎯 ДЕМО: Постоянный seed для консистентности")
    print("=" * 60)
    
    gen = SCWImageGenerator('demo_seed', 'demo')
    
    # Фиксированный персонаж для демонстрации
    char = CharacterAttributes(
        gender="f", age_group=1, ethnicity="w",
        hair_color="l", hair_length="l", hair_style="c",  # блондинка с кудрями
        makeup="m", tattoos="s", expression="f"           # макияж, тату, флирт
    )
    
    print("👩 Тестовый персонаж:")
    print(f"  Базовые: {char.gender}{char.age_group}{char.ethnicity}")
    print(f"  Волосы: {char.hair_color} (светлые), {char.hair_length} (длинные), {char.hair_style} (кудрявые)")
    print(f"  Детали: макияж {char.makeup}, тату {char.tattoos}, выражение {char.expression}")
    
    # Генерируем ID и seed несколько раз
    print("\n🔄 Тест консистентности:")
    for i in range(3):
        char_id = gen.generate_character_id(char)
        seed = gen.generate_character_seed(char_id)
        prompt = gen.build_base_prompt(char)
        print(f"  {i+1}. ID: {char_id} → seed: {seed}")
    
    # Демонстрируем фиксированный seed
    fixed_id = "demo123"
    seed1 = gen.generate_character_seed(fixed_id)
    seed2 = gen.generate_character_seed(fixed_id)
    
    print(f"\n✅ Фиксированный ID '{fixed_id}':")
    print(f"  Первый вызов: {seed1}")
    print(f"  Второй вызов: {seed2}")
    print(f"  Консистентность: {'ОК' if seed1 == seed2 else 'ОШИБКА'}")
    
    # Показываем промпт
    prompt = gen.build_base_prompt(char)
    print(f"\n📝 Детализированный промпт:")
    print(f"  {prompt}")
    print()

def demo_character_varieties():
    """Демонстрирует различные типы персонажей"""
    
    print("👥 ДЕМО: Разновидности персонажей")
    print("=" * 60)
    
    gen = SCWImageGenerator('demo_varieties', 'demo')
    
    # Простые персонажи
    simple_chars = get_simple_test_characters()
    print(f"🔰 Простые персонажи ({len(simple_chars)} шт):")
    for i, char in enumerate(simple_chars):
        char_id = gen.generate_character_id(char)
        seed = gen.generate_character_seed(char_id)
        print(f"  {i+1}. {char.gender}{char.age_group}{char.ethnicity} → ID: {char_id}, seed: {seed}")
    
    # Детализированные персонажи
    detailed_chars = get_detailed_test_characters()
    print(f"\n⭐ Детализированные персонажи ({len(detailed_chars)} шт):")
    for i, char in enumerate(detailed_chars[:3]):  # показываем первые 3
        char_id = gen.generate_character_id(char)
        seed = gen.generate_character_seed(char_id)
        details = f"стиль:{char.clothing_style}, макияж:{char.makeup}, тату:{char.tattoos}"
        print(f"  {i+1}. {char.gender}{char.age_group}{char.ethnicity} ({details}) → ID: {char_id}, seed: {seed}")
    
    # Экстремальные персонажи
    extreme_chars = get_extreme_test_characters()
    print(f"\n🔥 Экстремальные персонажи ({len(extreme_chars)} шт):")
    for i, char in enumerate(extreme_chars):
        char_id = gen.generate_character_id(char)
        seed = gen.generate_character_seed(char_id)
        details = f"размер:{char.breast_penis_size}, тату:{char.tattoos}, стиль:{char.clothing_style}"
        print(f"  {i+1}. {char.gender}{char.age_group}{char.ethnicity} ({details}) → ID: {char_id}, seed: {seed}")
    print()

def demo_prompt_details():
    """Демонстрирует детализированные промпты"""
    
    print("📝 ДЕМО: Детализированные промпты")
    print("=" * 60)
    
    gen = SCWImageGenerator('demo_prompts', 'demo')
    
    # Экстремально детализированный персонаж
    extreme_char = CharacterAttributes(
        gender="f", age_group=0, ethnicity="w",
        height="s", body_shape="s", breast_penis_size="s",
        hair_color="d", hair_length="l", hair_style="c",
        makeup="h", tattoos="l", piercings="m",
        expression="f", clothing_style="g"
    )
    
    print("🎭 Экстремально детализированная готическая девушка:")
    prompt = gen.build_base_prompt(extreme_char)
    print(f"Промпт: {prompt}")
    print(f"Длина: {len(prompt)} символов")
    print()
    
    # Простой персонаж для сравнения
    simple_char = CharacterAttributes(gender="f", age_group=2, ethnicity="w")
    simple_prompt = gen.build_base_prompt(simple_char)
    
    print("👩 Простая женщина:")
    print(f"Промпт: {simple_prompt}")
    print(f"Длина: {len(simple_prompt)} символов")
    print()
    
    print("📊 Сравнение:")
    print(f"  Детализированный: {len(prompt.split(','))} элементов")
    print(f"  Простой: {len(simple_prompt.split(','))} элементов")
    print(f"  Разница: +{len(prompt.split(',')) - len(simple_prompt.split(','))} деталей")

def main():
    """Запуск всех демонстраций"""
    
    print("🚀 SCW Image Generator: Демонстрация новых функций")
    print("="*70)
    print()
    
    demo_seed_consistency()
    print()
    demo_character_varieties()
    print()  
    demo_prompt_details()
    print()
    
    print("✨ Как использовать:")
    print("  python scw_image_generator.py --test --test-type simple")
    print("  python scw_image_generator.py --test --test-type detailed") 
    print("  python scw_image_generator.py --test --test-type extreme")
    print()
    print("🎉 Теперь каждый персонаж имеет постоянный seed для консистентных изображений!")

if __name__ == "__main__":
    main()
