"""
Упрощенный сервис заказов для лабораторной работы
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'password123')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'orders_db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Конфигурация зависимостей
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:8001')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:8002')
PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://localhost:8004')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, paid, cancelled, payment_failed
    total_amount = db.Column(db.Float, nullable=False)
    items = db.Column(db.Text)  # JSON строка с товарами
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

@app.route('/health', methods=['GET'])
def health():
    # Проверяем доступность зависимостей
    dependencies = {
        "user_service": check_service_health(USER_SERVICE_URL),
        "product_service": check_service_health(PRODUCT_SERVICE_URL),
        "payment_service": check_service_health(PAYMENT_SERVICE_URL)
    }
    
    all_healthy = all(dependencies.values())
    
    return jsonify({
        "status": "healthy" if all_healthy else "degraded",
        "service": "order-service",
        "dependencies": dependencies
    }), 200 if all_healthy else 503

def check_service_health(url):
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    # Получение и проверка заголовка авторизации
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token is required"}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    # Валидация токена через сервис пользователей
    user_info = validate_token(token)
    if not user_info:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = user_info.get('user_id')
    
    # Получение данных заказа
    data = request.get_json()
    if not data or 'items' not in data or not data['items']:
        return jsonify({"error": "Order items are required"}), 400
    
    # Валидация товаров и расчет суммы
    order_items = []
    total_amount = 0.0
    
    for item in data['items']:
        if 'product_id' not in item or 'quantity' not in item:
            return jsonify({"error": "Each item must have product_id and quantity"}), 400
        
        # Получение информации о товаре
        product_info = get_product_info(item['product_id'])
        if not product_info:
            return jsonify({"error": f"Product {item['product_id']} not found"}), 404
        
        # Проверка остатка
        if product_info['stock'] < item['quantity']:
            return jsonify({
                "error": f"Insufficient stock for product {product_info['name']}. Available: {product_info['stock']}, Requested: {item['quantity']}"
            }), 400
        
        # Расчет стоимости
        item_total = product_info['price'] * item['quantity']
        total_amount += item_total
        
        order_items.append({
            "product_id": item['product_id'],
            "product_name": product_info['name'],
            "quantity": item['quantity'],
            "price": product_info['price'],
            "item_total": item_total
        })
    
    # Создание заказа
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        items=json.dumps(order_items),
        status='pending'
    )
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        "message": "Order created successfully",
        "order_id": order.id,
        "total_amount": total_amount,
        "status": order.status,
        "items": order_items
    }), 201

@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    # Проверка авторизации
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token is required"}), 401
    
    token = auth_header.replace('Bearer ', '')
    user_info = validate_token(token)
    if not user_info:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    # Получение заказа
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    # Проверка прав доступа
    if order.user_id != user_info.get('user_id'):
        return jsonify({"error": "Access denied"}), 403
    
    return jsonify({
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "items": json.loads(order.items) if order.items else [],
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None
    }), 200

@app.route('/api/v1/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    # Проверка авторизации
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token is required"}), 401
    
    token = auth_header.replace('Bearer ', '')
    user_info = validate_token(token)
    if not user_info or user_info.get('user_id') != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    # Получение заказов пользователя
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    return jsonify({
        "orders": [{
            "id": o.id,
            "status": o.status,
            "total_amount": o.total_amount,
            "created_at": o.created_at.isoformat() if o.created_at else None
        } for o in orders],
        "count": len(orders)
    }), 200

@app.route('/api/v1/orders/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    # Проверка авторизации
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token is required"}), 401
    
    token = auth_header.replace('Bearer ', '')
    user_info = validate_token(token)
    if not user_info:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    # Получение заказа
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    # Проверка прав доступа
    if order.user_id != user_info.get('user_id'):
        return jsonify({"error": "Access denied"}), 403
    
    # Проверка статуса заказа
    if order.status != 'pending':
        return jsonify({"error": f"Cannot pay order with status '{order.status}'"}), 400
    
    # Вызов платежной системы
    payment_data = {
        "order_id": order.id,
        "amount": order.total_amount,
        "user_id": order.user_id
    }
    
    try:
        payment_response = requests.post(
            f"{PAYMENT_SERVICE_URL}/api/v1/payments",
            json=payment_data,
            timeout=5
        )
        
        if payment_response.status_code == 200:
            payment_result = payment_response.json()
            
            if payment_result.get('status') == 'success':
                # Обновление статуса заказа
                order.status = 'paid'
                
                # Обновление остатков товаров
                items = json.loads(order.items)
                for item in items:
                    update_product_stock(item['product_id'], -item['quantity'])
                
                db.session.commit()
                
                return jsonify({
                    "message": "Payment successful",
                    "order_id": order.id,
                    "new_status": order.status,
                    "payment_id": payment_result.get('payment_id')
                }), 200
            else:
                # Платеж не прошел
                order.status = 'payment_failed'
                db.session.commit()
                
                return jsonify({
                    "error": "Payment failed",
                    "order_id": order.id,
                    "new_status": order.status,
                    "payment_error": payment_result.get('error', 'Unknown error')
                }), 400
        else:
            # Ошибка при вызове платежной системы
            order.status = 'payment_failed'
            db.session.commit()
            
            return jsonify({
                "error": "Payment service error",
                "order_id": order.id,
                "new_status": order.status
            }), 502
            
    except requests.exceptions.RequestException as e:
        # Сетевая ошибка
        order.status = 'payment_failed'
        db.session.commit()
        
        return jsonify({
            "error": "Payment service unavailable",
            "order_id": order.id,
            "new_status": order.status
        }), 503

def validate_token(token):
    """Валидация токена через сервис пользователей"""
    try:
        response = requests.get(
            f"{USER_SERVICE_URL}/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=2
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return {"user_id": user_data.get('id')}
    except:
        pass
    
    return None

def get_product_info(product_id):
    """Получение информации о товаре"""
    try:
        response = requests.get(
            f"{PRODUCT_SERVICE_URL}/api/v1/products/{product_id}",
            timeout=2
        )
        
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None

def update_product_stock(product_id, delta):
    """Обновление остатков товара"""
    try:
        # Сначала получаем текущий остаток
        product_info = get_product_info(product_id)
        if product_info:
            new_stock = product_info['stock'] + delta
            
            response = requests.put(
                f"{PRODUCT_SERVICE_URL}/api/v1/products/{product_id}/stock",
                json={"stock": new_stock},
                timeout=2
            )
            
            return response.status_code == 200
    except:
        pass
    
    return False

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8003, debug=True)
