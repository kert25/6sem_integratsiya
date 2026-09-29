"""
Скрипт для запуска UI-тестов
"""
import subprocess
import sys
import os
from datetime import datetime


def run_tests():
    """Запуск тестов с разными параметрами"""
    
    print("=" * 60)
    print("Запуск UI-тестов")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Создаем директории для отчетов
    os.makedirs("reports", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Варианты запуска тестов
    test_configs = [
        {
            "name": "Все тесты",
            "command": ["pytest", "tests/", "-v"]
        },
        {
            "name": "Только smoke-тесты",
            "command": ["pytest", "tests/", "-m", "smoke", "-v"]
        },
        {
            "name": "Только тесты авторизации",
            "command": ["pytest", "tests/test_login.py", "-v"]
        },
        {
            "name": "Тесты с генерацией Allure отчета",
            "command": ["pytest", "tests/", "-v", "--alluredir=reports/allure_ui"]
        },
        {
            "name": "Тесты в Firefox",
            "command": ["pytest", "tests/", "-v", "--browser=firefox"]
        },
        {
            "name": "Тесты в headless режиме",
            "command": ["pytest", "tests/", "-v", "--headless"]
        }
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n{i}. {config['name']}")
        print("-" * 40)
        
        try:
            result = subprocess.run(config["command"], capture_output=True, text=True)
            
            print("СТАНДАРТНЫЙ ВЫВОД:")
            print(result.stdout[-1000:])  # Последние 1000 символов
            
            if result.stderr:
                print("\nОШИБКИ:")
                print(result.stderr[-500:])  # Последние 500 символов
            
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
