# -*- coding: utf-8 -*-
"""Скрипт запуска UI-тестов: полный прогон, smoke, по разделам, браузеры, Allure."""
import os
import subprocess
import sys
from datetime import datetime


def run_tests():
    """Запуск тестов с разными параметрами"""

    print("=" * 60)
    print("Запуск UI-тестов the-internet.herokuapp.com (вариант 9)")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    os.makedirs("reports", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)

    pytest_cmd = [sys.executable, "-m", "pytest"]

    test_configs = [
        {
            "name": "Все тесты (Chrome, headless)",
            "command": pytest_cmd + ["tests/", "--headless"],
        },
        {
            "name": "Только smoke-тесты",
            "command": pytest_cmd + ["tests/", "-m", "smoke", "--headless"],
        },
        {
            "name": "Тесты раздела Inputs",
            "command": pytest_cmd + ["tests/test_inputs.py", "--headless"],
        },
        {
            "name": "Тесты раздела Notification Messages",
            "command": pytest_cmd + ["tests/test_notification_messages.py", "--headless"],
        },
        {
            "name": "Тесты раздела Geolocation",
            "command": pytest_cmd + ["tests/test_geolocation.py", "--headless"],
        },
        {
            "name": "Все тесты в Firefox (headless)",
            "command": pytest_cmd + ["tests/", "--browser=firefox", "--headless"],
        },
        {
            "name": "Тесты с генерацией Allure-отчета",
            "command": pytest_cmd + ["tests/", "--headless",
                                     "--alluredir=reports/allure_ui"],
        },
    ]

    for i, config in enumerate(test_configs, 1):
        print(f"\n{i}. {config['name']}")
        print("-" * 40)

        try:
            result = subprocess.run(config["command"], capture_output=True, text=True)

            print("СТАНДАРТНЫЙ ВЫВОД (окончание):")
            print(result.stdout[-1500:])

            if result.stderr:
                print("\nОШИБКИ:")
                print(result.stderr[-500:])

            print(f"\nКод возврата: {result.returncode}")

        except Exception as e:
            print(f"Ошибка при запуске тестов: {e}")

    print("\n" + "=" * 60)
    print("Запуск тестов завершен")
    print("Отчеты доступны в директории 'reports/'")
    print("Скриншоты доступны в директории 'screenshots/'")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
