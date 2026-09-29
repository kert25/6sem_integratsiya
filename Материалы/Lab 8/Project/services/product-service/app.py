"""
Упрощенный сервис товаров для лабораторной работы
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'password123')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'products_db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "product-service"}), 200

@app.route('/api/v1/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    
    return jsonify({
        "products": [{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "category": p.category
        } for p in products],
        "count": len(products)
    }), 200

@app.route('/api/v1/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "category": product.category
    }), 200

@app.route('/api/v1/products/<int:product_id>/stock', methods=['PUT'])
def update_stock(product_id):
    data = request.get_json()
    
    if not data or 'stock' not in data:
        return jsonify({"error": "Stock amount is required"}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    product.stock = data['stock']
    db.session.commit()
    
    return jsonify({
        "message": "Stock updated successfully",
        "product_id": product.id,
        "new_stock": product.stock
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Добавляем тестовые товары, если их нет
        if Product.query.count() == 0:
            products = [
                Product(name="Ноутбук", description="Мощный ноутбук", price=50000, stock=10, category="Электроника"),
                Product(name="Смартфон", description="Флагманский смартфон", price=80000, stock=5, category="Электроника"),
                Product(name="Книга", description="Интересная книга", price=500, stock=100, category="Книги"),
                Product(name="Кофе", description="Свежеобжаренный кофе", price=350, stock=50, category="Продукты"),
            ]
            db.session.add_all(products)
            db.session.commit()
    
    app.run(host='0.0.0.0', port=8002, debug=True)
