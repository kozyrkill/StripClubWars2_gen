#!/usr/bin/env python3
"""
Тестовые персонажи для SCW Image Generator

Содержит детализированных персонажей для демонстрации различных возможностей
генератора, включая новые атрибуты и seed консистентность.
"""

from scw_image_generator import CharacterAttributes

def get_detailed_test_characters():
    """Возвращает список детализированных тестовых персонажей"""
    
    characters = []
    
    # 1. Очень молодая готическая девушка с малой грудью и татуировками
    characters.append(CharacterAttributes(
        gender="f", age_group=0, ethnicity="w",
        height="s", body_shape="s", breast_penis_size="s", skin_tone="l",
        hair_color="d", hair_length="l", hair_style="s", eye_color="d",
        makeup="m", tattoos="s", piercings="m",
        expression="f", clothing_style="g"
    ))
    
    # 2. Зрелая курчавая женщина с очень большой грудью
    characters.append(CharacterAttributes(
        gender="f", age_group=3, ethnicity="b",
        height="m", body_shape="c", breast_penis_size="x", skin_tone="d",
        hair_color="d", hair_length="m", hair_style="c", eye_color="d",
        makeup="h", tattoos="m", piercings="e",
        expression="s", clothing_style="e"
    ))
    
    # 3. Молодой азиатский мужчина с бородой и татуировками
    characters.append(CharacterAttributes(
        gender="m", age_group=2, ethnicity="a",
        height="t", body_shape="f", breast_penis_size="l", skin_tone="l",
        hair_color="d", hair_length="s", hair_style="n", eye_color="d",
        facial_hair="b", tattoos="l", piercings="n",
        expression="n", clothing_style="s"
    ))
    
    # 4. Спортивная латиноамериканка со средними параметрами
    characters.append(CharacterAttributes(
        gender="f", age_group=2, ethnicity="h",
        height="t", body_shape="f", breast_penis_size="m", skin_tone="m",
        hair_color="m", hair_length="s", hair_style="s", eye_color="m",
        makeup="l", tattoos="s", piercings="e",
        expression="h", clothing_style="s"
    ))
    
    # 5. Зрелый ближневосточный мужчина с полной бородой
    characters.append(CharacterAttributes(
        gender="m", age_group=4, ethnicity="r",
        height="m", body_shape="n", breast_penis_size="m", skin_tone="m",
        hair_color="d", hair_length="s", hair_style="n", eye_color="d",
        facial_hair="f", tattoos="n", piercings="n",
        expression="n", clothing_style="e"
    ))
    
    # 6. Молодая блондинка с волнистыми волосами и флирт
    characters.append(CharacterAttributes(
        gender="f", age_group=1, ethnicity="w",
        height="m", body_shape="c", breast_penis_size="l", skin_tone="l",
        hair_color="l", hair_length="l", hair_style="w", eye_color="l",
        makeup="m", tattoos="n", piercings="e",
        expression="f", clothing_style="c"
    ))
    
    return characters

def get_simple_test_characters():
    """Возвращает простые персонажи для быстрого тестирования"""
    
    characters = []
    
    # Простая молодая девушка
    characters.append(CharacterAttributes(
        gender="f", age_group=0, ethnicity="w",
        breast_penis_size="s"
    ))
    
    # Женщина с большой грудью  
    characters.append(CharacterAttributes(
        gender="f", age_group=2, ethnicity="w",
        body_shape="c", breast_penis_size="x"
    ))
    
    # Мужчина
    characters.append(CharacterAttributes(
        gender="m", age_group=4, ethnicity="a",
        body_shape="f", breast_penis_size="l"
    ))
    
    return characters

def get_extreme_test_characters():
    """Возвращает персонажи с экстремальными характеристиками"""
    
    characters = []
    
    # Экстремальная готическая девушка
    characters.append(CharacterAttributes(
        gender="f", age_group=0, ethnicity="w",
        height="s", body_shape="s", breast_penis_size="s", skin_tone="l",
        hair_color="d", hair_length="l", hair_style="s", eye_color="d",
        makeup="h", tattoos="l", piercings="m",
        expression="f", clothing_style="g"
    ))
    
    # Экстремально мускулистый мужчина
    characters.append(CharacterAttributes(
        gender="m", age_group=3, ethnicity="b",
        height="t", body_shape="f", breast_penis_size="x", skin_tone="d",
        hair_color="d", hair_length="b", hair_style="n", eye_color="d",
        facial_hair="f", tattoos="l", piercings="e",
        expression="n", clothing_style="s"
    ))
    
    # Экстремально пышная женщина
    characters.append(CharacterAttributes(
        gender="f", age_group=4, ethnicity="h",
        height="s", body_shape="c", breast_penis_size="x", skin_tone="m",
        hair_color="l", hair_length="l", hair_style="c", eye_color="l",
        makeup="h", tattoos="m", piercings="m",
        expression="f", clothing_style="e"
    ))
    
    return characters

if __name__ == "__main__":
    print("🧪 Доступные наборы тестовых персонажей:")
    print(f"  Детализированные: {len(get_detailed_test_characters())} персонажей")
    print(f"  Простые: {len(get_simple_test_characters())} персонажей") 
    print(f"  Экстремальные: {len(get_extreme_test_characters())} персонажей")
    
    print("\n👥 Примеры детализированных персонажей:")
    for i, char in enumerate(get_detailed_test_characters()[:2]):
        print(f"  {i+1}. {char.gender}{char.age_group}{char.ethnicity} - "
              f"стиль: {char.clothing_style}, волосы: {char.hair_style}, "
              f"макияж: {char.makeup}, татуировки: {char.tattoos}")
