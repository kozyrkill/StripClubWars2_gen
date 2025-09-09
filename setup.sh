#!/bin/bash
# Скрипт для установки зависимостей SCW Image Generator в виртуальное окружение

echo "Установка зависимостей для SCW Character Image Pack Generator..."

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не найден. Установите Python 3.8 или выше."
    exit 1
fi

# Создание виртуального окружения если его нет
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Ошибка создания виртуального окружения"
        exit 1
    fi
fi

# Активация виртуального окружения и установка зависимостей
echo "Активация виртуального окружения и установка зависимостей..."
source venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Зависимости установлены успешно в виртуальное окружение!"
    echo ""
    echo "Для запуска генератора:"
    echo "1. Активируйте виртуальное окружение:"
    echo "   source venv/bin/activate"
    echo "2. Убедитесь что Stable Diffusion WebUI запущен с флагом --api"
    echo "3. Проверьте подключение: python test_webui_connection.py"
    echo "4. Запустите генератор: python scw_image_generator.py --test"
    echo ""
    echo "Или используйте activate.sh для быстрой активации"
else
    echo "✗ Ошибка установки зависимостей"
    exit 1
fi
