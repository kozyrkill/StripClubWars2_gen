# Быстрый старт

## 1. Установка в виртуальное окружение

```bash
# Автоматическая установка (создает venv и устанавливает зависимости)
bash setup.sh
```

## 2. Запуск Stable Diffusion WebUI

```bash
# В директории webui запустите:
python launch.py --api
```

## 3. Активация окружения и проверка подключения

```bash
# Способ 1: Быстрая активация
bash activate.sh

# Способ 2: Ручная активация
source venv/bin/activate
python test_webui_connection.py
```

## 4. Первая генерация

```bash
# В активированном venv:
python scw_image_generator.py --test

# Или из конфигурации:
python scw_image_generator.py --config character_config.json
```

## Файлы проекта

- `scw_image_generator.py` - основной генератор
- `character_config.json` - конфигурация персонажей
- `requirements.txt` - зависимости Python
- `setup.sh` - скрипт установки
- `test_webui_connection.py` - проверка WebUI
- `README.md` - полная документация

## Результат

Генерируются изображения в формате SCW:
- `custom-01000-f2w-mnmml-llm-u-head.png` (голова)
- `custom-01000-z0-cas.png` (повседневная одежда)
- `custom-01000-z3-uw.png` (нижнее белье)
- `custom-01000-z9-nude.png` (обнаженная)
- и другие позы...

Готовые изображения можно скопировать в игру!
