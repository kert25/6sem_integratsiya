#!/bin/bash
# Скрипт для запуска тестов

echo "=== Запуск API-тестов ==="

# Создаем директорию для отчетов
mkdir -p reports

export PYTHONPATH=$PYTHONPATH:.

# Запускаем тесты
echo "1. Запуск всех тестов..."
pytest tests/ -v

echo "2. Запуск только smoke-тестов..."
pytest tests/ -m smoke -v

echo "3. Запуск тестов с генерацией Allure отчета..."
pytest tests/ -v --alluredir=reports/allure-results

echo "=== Тестирование завершено ==="
echo "Отчеты доступны в директории reports/"