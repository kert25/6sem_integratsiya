"""
Функции для проверки тест-кейсов лабораторной работы №3.
Содержат преднамеренные ошибки для обучения.
"""

def calculate_delivery(distance_km, weight_kg, urgency):
    """
    Вариант 1: Расчет стоимости доставки.
    Вход:
      distance_km: float (1-5000)
      weight_kg: float (0.1-100)
      urgency: str ("Обычная", "Экспресс", "Срочная")
    Возвращает: float (стоимость) или строку с ошибкой.
    """
    # Преднамеренные ошибки:
    # 1. Не проверяется верхняя граница расстояния (5000)
    # 2. Ошибка в границе для веса (>50 вместо >=50)
    # 3. Неправильный коэффициент для срочности
    
    if distance_km < 1 or weight_kg < 0.1 or weight_kg > 100:
        return "Ошибка: неверные входные данные"
    
    # Базовая стоимость по зонам
    if distance_km <= 50:
        base_rate = 5  # руб/км
    elif distance_km <= 200:  # Ошибка: должно быть 51-200
        base_rate = 8
    else:
        base_rate = 12
    
    base_cost = distance_km * base_rate
    
    # Надбавка за вес
    if weight_kg > 10:
        base_cost += (weight_kg - 10) * 50  # 50 руб/кг сверх 10
    
    # Коэффициент сложности (ошибка в условии)
    if weight_kg > 50 or distance_km > 3000:  # Должно быть >=50
        base_cost *= 1.5
    
    # Коэффициент срочности
    urgency_multiplier = 1.0
    if urgency == "Экспресс":
        urgency_multiplier = 1.3  # Должно быть 1.3
    elif urgency == "Срочная":
        urgency_multiplier = 1.7  # Должно быть 1.7
    
    # Проверка доступности срочной доставки
    if distance_km > 2000 and urgency != "Обычная":
        return "Ошибка: срочная доставка недоступна для данного расстояния"
    
    final_cost = base_cost * urgency_multiplier
    
    # Минимальная стоимость
    if final_cost < 300:
        return 300.0
    
    return round(final_cost, 2)


def check_password_strength(password):
    """
    Вариант 2: Проверка сложности пароля.
    Вход: str
    Возвращает: tuple (оценка: "Слабый"/"Средний"/"Сильный", рекомендации)
    """
    # Преднамеренные ошибки:
    # 1. Неправильная граница для длины в слабом пароле
    # 2. Не проверяется наличие спецсимволов для средней сложности
    # 3. Ошибка в проверке повторяющихся символов
    
    recommendations = []
    
    # Проверка на распространенные пароли
    weak_passwords = ["123456", "password", "qwerty", "admin"]
    if password in weak_passwords:
        return ("Слабый", ["Пароль слишком распространен"])
    
    # Проверка длины
    if len(password) < 8:  # Ошибка: должно быть <= 8
        recommendations.append("Увеличьте длину пароля до 8+ символов")
        return ("Слабый", recommendations)
    
    # Проверка на только цифры или только буквы
    if password.isdigit() or password.isalpha():
        recommendations.append("Используйте буквы и цифры")
        # Ошибка: должен быть слабым, но возвращаем средний
        return ("Средний", recommendations)
    
    # Проверка на наличие разных категорий символов
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*" for c in password)
    
    # Проверка на повторяющиеся символы (ошибка в логике)
    for i in range(len(password) - 2):
        if password[i] == password[i+1] == password[i+2]:
            recommendations.append("Избегайте повторяющихся символов")
            # Должен быть слабым, но продолжаем
    
    # Определение сложности
    if len(password) >= 12 and has_upper and has_lower and has_digit and has_special:
        if not recommendations:
            recommendations.append("Пароль отличный!")
        return ("Сильный", recommendations)
    elif len(password) >= 8 and has_digit and (has_upper or has_lower):
        if not recommendations:
            recommendations.append("Пароль хороший, можно усилить")
        return ("Средний", recommendations)
    else:
        return ("Слабый", recommendations + ["Добавьте цифры и буквы разных регистров"])


def calculate_bonus(purchase_amount, category, client_status):
    """
    Вариант 3: Расчет бонусных баллов.
    Вход:
      purchase_amount: float (1-1_000_000)
      category: str ("Электроника", "Продукты", "Одежда")
      client_status: str ("Новый", "Постоянный", "VIP")
    Возвращает: float (бонус в рублях) или сообщение об ошибке
    """
    # Преднамеренные ошибки:
    # 1. Не проверяется граница для нового клиента (1000 руб)
    # 2. Неправильный коэффициент для VIP
    # 3. Ошибка в максимальном бонусе
    
    if purchase_amount < 1 or purchase_amount > 1000000:
        return "Ошибка: неверная сумма покупки"
    
    # Базовый процент
    bonus_percent = 0.01  # 1%
    
    # Надбавка за категорию
    if category == "Электроника":
        bonus_percent += 0.005  # 0.5%
    elif category == "Одежда":  # Ошибка: для одежды не должно быть надбавки
        bonus_percent += 0.002
    
    # Надбавка за статус
    if client_status == "Постоянный":
        bonus_percent += 0.005  # 0.5%
    elif client_status == "VIP":
        bonus_percent += 0.01  # Ошибка: должно быть 0.015 (1.5%)
    
    # Расчет бонуса
    bonus = purchase_amount * bonus_percent
    
    # Проверка минимальной суммы для новых клиентов
    if client_status == "Новый" and purchase_amount < 1000:
        return "Бонус не начисляется: минимальная сумма 1000 руб. для новых клиентов"
    
    # Максимальный бонус (ошибка: должно быть 5000)
    if bonus > 10000:
        bonus = 10000
    
    return round(bonus, 2)


def calculate_insurance(country_group, age, days, has_sport):
    """
    Вариант 4: Расчет страховки для путешественников.
    Вход:
      country_group: int (1, 2, 3)
      age: int (0-120)
      days: int (1-365)
      has_sport: bool
    Возвращает: float (стоимость) или сообщение об ошибке
    """
    # Преднамеренные ошибки:
    # 1. Не проверяется верхняя граница возраста
    # 2. Неправильный тариф для группы 3
    # 3. Ошибка в минимальной стоимости
    
    if not (1 <= country_group <= 3):
        return "Ошибка: неверная группа стран"
    
    if age < 0 or age > 120:  # Ошибка: должно быть 0-120
        return "Ошибка: неверный возраст"
    
    if days < 1 or days > 365:
        return "Ошибка: неверное количество дней"
    
    # Базовый тариф
    if country_group == 1:
        daily_rate = 50
    elif country_group == 2:
        daily_rate = 70
    else:  # группа 3
        daily_rate = 80  # Ошибка: должно быть 90
    
    # Возрастной коэффициент
    if age <= 17:
        age_coef = 1.0
    elif age <= 65:
        age_coef = 1.2
    else:
        age_coef = 1.5
    
    # Расчет
    cost = daily_rate * days * age_coef
    
    # Надбавка за спорт
    if has_sport:
        cost *= 1.2
    
    # Минимальная и максимальная стоимость
    if cost < 500:
        cost = 500
    elif cost > 100000:
        cost = 100000
    
    return round(cost, 2)


# Функция для тестирования студентами
def run_tests():
    """Запуск примеров тестов для демонстрации"""
    print("=== Тестирование функций для Л/Р №3 ===")
    
    print("\n1. Расчет доставки:")
    print(f"  1 км, 0.1 кг, Обычная: {calculate_delivery(1, 0.1, 'Обычная')}")
    print(f"  100 км, 60 кг, Обычная: {calculate_delivery(100, 60, 'Обычная')}")
    
    print("\n2. Проверка пароля:")
    print(f"  '123': {check_password_strength('123')}")
    print(f"  'Password123': {check_password_strength('Password123')}")
    
    print("\n3. Расчет бонуса:")
    print(f"  5000 руб, Электроника, VIP: {calculate_bonus(5000, 'Электроника', 'VIP')}")
    
    print("\n4. Расчет страховки:")
    print(f"  Группа 1, 25 лет, 10 дней, без спорта: {calculate_insurance(1, 25, 10, False)}")


if __name__ == "__main__":
    run_tests()