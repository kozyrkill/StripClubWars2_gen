#!/bin/bash
# Скрипт для быстрой активации виртуального окружения

if [ ! -d "venv" ]; then
    echo "⚠️  Виртуальное окружение не найдено!"
    echo "Сначала запустите: bash setup.sh"
    exit 1
fi

echo "🟢 Активация виртуального окружения..."
source venv/bin/activate

echo "✅ Виртуальное окружение активировано!"
echo ""
echo "Доступные команды:"
echo "  python test_webui_connection.py     - проверить WebUI"
echo "  python scw_image_generator.py --test  - генерировать тест"
echo "  python scw_image_generator.py --config character_config.json  - генерировать из конфигурации"
echo ""
echo "Для деактивации введите: deactivate"

# Запускаем новую оболочку с активированным окружением
exec bash
