"""
Лабораторный сервер REST API для тестирования
Интеграция и тестирование программных систем - Л/Р №2
"""
import json
import uuid
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)  # Разрешаем кросс-доменные запросы

# ========== БАЗА ДАННЫХ В ПАМЯТИ ==========

# Вариант 1: Задачи (To-Do List)
tasks = {
    1: {"id": 1, "title": "Изучить REST API", "completed": False, "userId": 1},
    2: {"id": 2, "title": "Написать тесты для API", "completed": True, "userId": 1},
    3: {"id": 3, "title": "Протестировать интеграцию", "completed": False, "userId": 2}
}
task_id_counter = 4

# Вариант 2: Пользователи и аутентификация
users = {
    1: {"id": 1, "email": "student@university.ru", "password": "password123", "name": "Иван Иванов"},
    2: {"id": 2, "email": "teacher@university.ru", "password": "securepass", "name": "Мария Петрова"}
}
active_tokens = {}  # token -> user_id

# Вариант 3: Интернет-магазин
products = [
    {"id": 1, "name": "Ноутбук", "price": 50000, "category": "Электроника", "stock": 10},
    {"id": 2, "name": "Книга по тестированию", "price": 1500, "category": "Книги", "stock": 25},
    {"id": 3, "name": "Кофе", "price": 350, "category": "Продукты", "stock": 100},
    {"id": 4, "name": "Футболка", "price": 1200, "category": "Одежда", "stock": 0}  # Нет в наличии
]

carts = {}  # session_id -> [{"productId": X, "quantity": Y}]

# Вариант 4: Погодный сервис (mock)
weather_data = {
    "Moscow": {"temp": 15, "humidity": 65, "conditions": "облачно"},
    "London": {"temp": 10, "humidity": 80, "conditions": "дождь"},
    "Tokyo": {"temp": 22, "humidity": 50, "conditions": "ясно"}
}

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def require_auth(f):
    """Декоратор для проверки аутентификации"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "Требуется аутентификация"}), 401
        
        token = token.replace('Bearer ', '')
        if token not in active_tokens:
            return jsonify({"error": "Неверный или просроченный токен"}), 401
        
        request.user_id = active_tokens[token]
        return f(*args, **kwargs)
    return decorated

def get_cart():
    """Получение или создание корзины для сессии"""
    session_id = request.headers.get('X-Session-Id')
    if not session_id:
        return None
    if session_id not in carts:
        carts[session_id] = []
    return carts[session_id]

def validate_product_data(data):
    """Валидация данных товара"""
    errors = []
    if 'name' not in data or not data['name'].strip():
        errors.append("Требуется название товара")
    if 'price' not in data or not isinstance(data['price'], (int, float)) or data['price'] <= 0:
        errors.append("Цена должна быть положительным числом")
    if 'stock' not in data or not isinstance(data['stock'], int) or data['stock'] < 0:
        errors.append("Количество должно быть неотрицательным целым числом")
    return errors

# ========== ВАРИАНТ 1: API УПРАВЛЕНИЯ ЗАДАЧАМИ ==========

@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    """Получить список задач с фильтрацией"""
    completed = request.args.get('completed')
    user_id = request.args.get('userId')
    
    filtered_tasks = list(tasks.values())
    
    if completed is not None:
        completed_bool = completed.lower() == 'true'
        filtered_tasks = [t for t in filtered_tasks if t['completed'] == completed_bool]
    
    if user_id is not None:
        try:
            user_id_int = int(user_id)
            filtered_tasks = [t for t in filtered_tasks if t.get('userId') == user_id_int]
        except ValueError:
            pass
    
    return jsonify({"tasks": filtered_tasks, "count": len(filtered_tasks)})

@app.route('/api/v1/tasks', methods=['POST'])
def create_task():
    """Создать новую задачу"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Требуется JSON тело запроса"}), 400
        
        # Валидация
        if 'title' not in data or not data['title'].strip():
            return jsonify({"error": "Поле 'title' обязательно и не может быть пустым"}), 400
        
        # Создание задачи
        global task_id_counter
        new_task = {
            "id": task_id_counter,
            "title": data['title'].strip(),
            "completed": data.get('completed', False),
            "userId": data.get('userId', 1),
            "createdAt": datetime.now().isoformat()
        }
        
        tasks[task_id_counter] = new_task
        task_id_counter += 1
        
        return jsonify(new_task), 201
    except Exception as e:
        return jsonify({"error": f"Ошибка сервера: {str(e)}"}), 500

@app.route('/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Получить задачу по ID"""
    if task_id not in tasks:
        return jsonify({"error": "Задача не найдена"}), 404
    
    return jsonify(tasks[task_id])

@app.route('/api/v1/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Обновить задачу целиком"""
    if task_id not in tasks:
        return jsonify({"error": "Задача не найдена"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Требуется JSON тело запроса"}), 400
    
    if 'title' not in data or not data['title'].strip():
        return jsonify({"error": "Поле 'title' обязательно"}), 400
    
    tasks[task_id].update({
        "title": data['title'].strip(),
        "completed": data.get('completed', tasks[task_id]['completed']),
        "userId": data.get('userId', tasks[task_id].get('userId', 1)),
        "updatedAt": datetime.now().isoformat()
    })
    
    return jsonify(tasks[task_id])

@app.route('/api/v1/tasks/<int:task_id>', methods=['PATCH'])
def patch_task(task_id):
    """Частично обновить задачу"""
    if task_id not in tasks:
        return jsonify({"error": "Задача не найдена"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Требуется JSON тело запроса"}), 400
    
    # Обновляем только переданные поля
    if 'title' in data and data['title'] is not None:
        if not data['title'].strip():
            return jsonify({"error": "Поле 'title' не может быть пустым"}), 400
        tasks[task_id]['title'] = data['title'].strip()
    
    if 'completed' in data:
        tasks[task_id]['completed'] = bool(data['completed'])
    
    tasks[task_id]['updatedAt'] = datetime.now().isoformat()
    
    return jsonify(tasks[task_id])

@app.route('/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Удалить задачу"""
    if task_id not in tasks:
        return jsonify({"error": "Задача не найдена"}), 404
    
    deleted_task = tasks.pop(task_id)
    return jsonify({"message": "Задача удалена", "task": deleted_task})

# ========== ВАРИАНТ 2: API АУТЕНТИФИКАЦИИ ==========

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Требуются email и password"}), 400
    
    # Проверка формата email
    if '@' not in data['email']:
        return jsonify({"error": "Неверный формат email"}), 400
    
    # Проверка существования пользователя
    for user in users.values():
        if user['email'] == data['email']:
            return jsonify({"error": "Пользователь с таким email уже существует"}), 409
    
    # Создание пользователя
    new_id = max(users.keys()) + 1 if users else 1
    users[new_id] = {
        "id": new_id,
        "email": data['email'],
        "password": data['password'],  # В реальном приложении хранить хэш!
        "name": data.get('name', ''),
        "registeredAt": datetime.now().isoformat()
    }
    
    return jsonify({"message": "Пользователь зарегистрирован", "userId": new_id}), 201

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Аутентификация пользователя"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Требуются email и password"}), 400
    
    # Поиск пользователя
    user = None
    for u in users.values():
        if u['email'] == data['email'] and u['password'] == data['password']:
            user = u
            break
    
    if not user:
        return jsonify({"error": "Неверный email или пароль"}), 401
    
    # Создание токена
    token = str(uuid.uuid4())
    active_tokens[token] = user['id']
    
    return jsonify({
        "token": token,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "name": user['name']
        }
    })

@app.route('/api/v1/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Выход из системы"""
    token = request.headers.get('Authorization').replace('Bearer ', '')
    if token in active_tokens:
        del active_tokens[token]
    return jsonify({"message": "Успешный выход"})

@app.route('/api/v1/users/me', methods=['GET'])
@require_auth
def get_current_user():
    """Получение данных текущего пользователя"""
    user_id = request.user_id
    user = users.get(user_id)
    
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    # Не возвращаем пароль
    user_data = {k: v for k, v in user.items() if k != 'password'}
    return jsonify(user_data)

# ========== ВАРИАНТ 3: API ИНТЕРНЕТ-МАГАЗИНА ==========

@app.route('/api/v1/products', methods=['GET'])
def get_products():
    """Получить список товаров с фильтрацией"""
    category = request.args.get('category')
    min_price = request.args.get('minPrice')
    max_price = request.args.get('maxPrice')
    in_stock = request.args.get('inStock')
    
    filtered_products = products.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
    
    if min_price:
        try:
            min_price = float(min_price)
            filtered_products = [p for p in filtered_products if p['price'] >= min_price]
        except ValueError:
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            filtered_products = [p for p in filtered_products if p['price'] <= max_price]
        except ValueError:
            pass
    
    if in_stock and in_stock.lower() == 'true':
        filtered_products = [p for p in filtered_products if p['stock'] > 0]
    
    return jsonify({"products": filtered_products, "count": len(filtered_products)})

@app.route('/api/v1/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Получить товар по ID"""
    for product in products:
        if product['id'] == product_id:
            return jsonify(product)
    
    return jsonify({"error": "Товар не найден"}), 404

@app.route('/api/v1/cart', methods=['GET'])
def get_cart_items():
    """Получить содержимое корзины"""
    cart = get_cart()
    if cart is None:
        return jsonify({"error": "Требуется заголовок X-Session-Id"}), 400
    
    # Добавляем информацию о товарах
    cart_with_details = []
    total = 0
    
    for item in cart:
        product = next((p for p in products if p['id'] == item['productId']), None)
        if product:
            item_with_details = item.copy()
            item_with_details['product'] = product
            item_with_details['subtotal'] = product['price'] * item['quantity']
            cart_with_details.append(item_with_details)
            total += item_with_details['subtotal']
    
    return jsonify({
        "items": cart_with_details,
        "total": total,
        "count": len(cart)
    })

@app.route('/api/v1/cart/items', methods=['POST'])
def add_to_cart():
    """Добавить товар в корзину"""
    cart = get_cart()
    if cart is None:
        return jsonify({"error": "Требуется заголовок X-Session-Id"}), 400
    
    data = request.get_json()
    if not data or 'productId' not in data or 'quantity' not in data:
        return jsonify({"error": "Требуются productId и quantity"}), 400
    
    product_id = data['productId']
    quantity = data['quantity']
    
    # Проверка существования товара
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Товар не найден"}), 404
    
    # Проверка наличия на складе
    if product['stock'] < quantity:
        return jsonify({"error": "Недостаточно товара на складе"}), 409
    
    # Проверка, есть ли уже товар в корзине
    for item in cart:
        if item['productId'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({"productId": product_id, "quantity": quantity})
    
    return jsonify({
        "message": "Товар добавлен в корзину",
        "cart": cart
    }), 201

@app.route('/api/v1/cart/items/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    """Удалить товар из корзины"""
    cart = get_cart()
    if cart is None:
        return jsonify({"error": "Требуется заголовок X-Session-Id"}), 400
    
    # Поиск и удаление товара
    for i, item in enumerate(cart):
        if item['productId'] == product_id:
            removed = cart.pop(i)
            return jsonify({
                "message": "Товар удален из корзины",
                "removedItem": removed,
                "cart": cart
            })
    
    return jsonify({"error": "Товар не найден в корзине"}), 404

# ========== ВАРИАНТ 4: API ПОГОДНОГО СЕРВИСА ==========

@app.route('/api/v1/weather', methods=['GET'])
def get_weather():
    """Получить погоду по городу"""
    city = request.args.get('q')
    units = request.args.get('units', 'metric')
    
    if not city:
        return jsonify({"error": "Требуется параметр q (город)"}), 400
    
    city_key = city.capitalize()
    if city_key not in weather_data:
        # Генерация mock-данных для неизвестного города
        import random
        weather_data[city_key] = {
            "temp": random.randint(-10, 35),
            "humidity": random.randint(30, 95),
            "conditions": random.choice(["ясно", "облачно", "дождь", "снег"])
        }
    
    data = weather_data[city_key].copy()
    
    # Конвертация единиц измерения (для демонстрации)
    if units == 'imperial':
        data['temp'] = round(data['temp'] * 9/5 + 32, 1)
        data['units'] = 'imperial'
    else:
        data['units'] = 'metric'
    
    data['city'] = city_key
    data['timestamp'] = datetime.now().isoformat()
    
    return jsonify(data)

@app.route('/api/v1/forecast', methods=['GET'])
def get_forecast():
    """Получить прогноз погоды"""
    city = request.args.get('q')
    days = int(request.args.get('days', 3))
    
    if not city:
        return jsonify({"error": "Требуется параметр q (город)"}), 400
    
    # Генерация mock-прогноза
    import random
    forecast = []
    base_temp = random.randint(10, 25)
    
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).date()
        forecast.append({
            "date": date.isoformat(),
            "temp_min": base_temp + random.randint(-3, 0),
            "temp_max": base_temp + random.randint(0, 3),
            "conditions": random.choice(["ясно", "облачно", "дождь", "снег"]),
            "humidity": random.randint(50, 90)
        })
    
    return jsonify({
        "city": city.capitalize(),
        "forecast": forecast,
        "days": days
    })

# ========== ОБЩИЕ ЭНДПОИНТЫ ==========

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервера"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "endpoints": {
            "tasks": "/api/v1/tasks",
            "auth": "/api/v1/auth/*",
            "products": "/api/v1/products",
            "cart": "/api/v1/cart",
            "weather": "/api/v1/weather"
        }
    })

@app.route('/api/v1/reset', methods=['POST'])
def reset_data():
    """Сброс всех данных (только для тестирования!)"""
    global tasks, task_id_counter, carts
    
    tasks = {
        1: {"id": 1, "title": "Изучить REST API", "completed": False, "userId": 1},
        2: {"id": 2, "title": "Написать тесты для API", "completed": True, "userId": 1}
    }
    task_id_counter = 3
    carts.clear()
    
    return jsonify({"message": "Данные сброшены"})

# ========== ОБРАБОТЧИКИ ОШИБОК ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Ресурс не найден"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Метод не разрешен"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# ========== ЗАПУСК СЕРВЕРА ==========

if __name__ == '__main__':
    print("=" * 60)
    print("Лабораторный сервер REST API для тестирования")
    print("Дисциплина: Интеграция и тестирование программных систем")
    print("Л/Р №2: Тестирование API как основа интеграции")
    print("=" * 60)
    print("\nДоступные эндпоинты:")
    print("  GET  /api/v1/tasks           - Список задач")
    print("  POST /api/v1/tasks           - Создать задачу")
    print("  GET  /api/v1/tasks/{id}      - Получить задачу")
    print("  PUT  /api/v1/tasks/{id}      - Обновить задачу")
    print("  DELETE /api/v1/tasks/{id}    - Удалить задачу")
    print("\n  POST /api/v1/auth/register  - Регистрация")
    print("  POST /api/v1/auth/login      - Вход")
    print("  GET  /api/v1/users/me        - Данные пользователя (требует токен)")
    print("\n  GET  /api/v1/products       - Каталог товаров")
    print("  GET  /api/v1/cart            - Корзина (требует X-Session-Id)")
    print("  POST /api/v1/cart/items      - Добавить в корзину")
    print("\n  GET  /api/v1/weather        - Погода по городу")
    print("  GET  /api/v1/health          - Проверка здоровья")
    print("  POST /api/v1/reset           - Сброс данных (для тестов)")
    print("\nСервер запущен: http://localhost:5000")
    print("Документация Swagger: http://localhost:5000/api/v1/swagger")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)