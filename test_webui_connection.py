#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки подключения к Stable Diffusion WebUI
"""

import requests
import json

WEBUI_URL = "http://localhost:7860"
WEBUI_API_URL = f"{WEBUI_URL}/sdapi/v1"

def test_webui_connection():
    """Проверяет подключение к WebUI и выводит информацию о системе"""
    
    print("🔍 Проверка подключения к Stable Diffusion WebUI...")
    print(f"URL: {WEBUI_URL}")
    print("-" * 50)
    
    try:
        # Проверка базового подключения
        print("1. Проверка базового подключения...")
        response = requests.get(f"{WEBUI_API_URL}/options", timeout=10)
        
        if response.status_code == 200:
            print("✅ WebUI API доступен!")
        else:
            print(f"❌ WebUI API недоступен. Статус: {response.status_code}")
            return False
            
        # Получение информации о модели
        print("\n2. Информация о модели...")
        try:
            options = response.json()
            model_name = options.get("sd_model_checkpoint", "Неизвестно")
            print(f"📊 Активная модель: {model_name}")
        except:
            print("⚠️  Не удалось получить информацию о модели")
        
        # Проверка доступности txt2img API
        print("\n3. Проверка txt2img API...")
        test_payload = {
            "prompt": "test",
            "steps": 1,
            "width": 64,
            "height": 64,
            "cfg_scale": 1,
        }
        
        response = requests.post(f"{WEBUI_API_URL}/txt2img", json=test_payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ txt2img API работает!")
            result = response.json()
            if result.get("images"):
                print("✅ Генерация изображений доступна!")
            else:
                print("⚠️  API отвечает, но изображения не генерируются")
        else:
            print(f"❌ txt2img API недоступен. Статус: {response.status_code}")
            if response.text:
                print(f"Ошибка: {response.text}")
            return False
            
        # Получение списка сэмплеров
        print("\n4. Доступные сэмплеры...")
        try:
            response = requests.get(f"{WEBUI_API_URL}/samplers", timeout=10)
            if response.status_code == 200:
                samplers = response.json()
                sampler_names = [s["name"] for s in samplers]
                print(f"📋 Найдено {len(sampler_names)} сэмплеров:")
                for name in sampler_names[:5]:  # Показываем первые 5
                    print(f"   • {name}")
                if len(sampler_names) > 5:
                    print(f"   ... и еще {len(sampler_names) - 5}")
        except Exception as e:
            print(f"⚠️  Не удалось получить список сэмплеров: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 WebUI готов к работе!")
        print("Теперь вы можете запустить генератор персонажей:")
        print("python scw_image_generator.py --test")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к WebUI")
        print("\n💡 Убедитесь что:")
        print("1. Stable Diffusion WebUI запущен")
        print("2. WebUI запущен с флагом --api:")
        print("   python launch.py --api")
        print("3. WebUI доступен по адресу http://localhost:7860")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Время ожидания подключения истекло")
        print("WebUI может быть перегружен или слишком медленно отвечать")
        return False
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def main():
    """Основная функция тестирования"""
    success = test_webui_connection()
    
    if not success:
        print("\n🔧 Инструкции по запуску WebUI с API:")
        print("1. Перейдите в директорию Stable Diffusion WebUI")
        print("2. Запустите: python launch.py --api")
        print("3. Дождитесь полной загрузки")
        print("4. Проверьте что интерфейс доступен в браузере")
        print("5. Запустите этот скрипт снова")
        
        exit(1)

if __name__ == "__main__":
    main()
