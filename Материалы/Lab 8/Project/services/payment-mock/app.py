"""
Mock платежной системы для лабораторной работы
"""
from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

# Настройки поведения мока (можно менять через переменные окружения)
SUCCESS_RATE = 0.8  # 80% успешных платежей
AVERAGE_DELAY = 1.0  # Средняя задержка в секундах
FAILURE_MODES = ['timeout', 'error', 'declined']  # Режимы отказа

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "payment-mock"}), 200

@app.route('/api/v1/payments', methods=['POST'])
def process_payment():
    data = request.get_json()
    
    if not data or 'order_id' not in data or 'amount' not in data:
        return jsonify({"error": "Invalid payment data"}), 400
    
    # Имитация задержки
    delay = random.uniform(AVERAGE_DELAY * 0.5, AVERAGE_DELAY * 1.5)
    time.sleep(delay)
    
    # Решение об успешности платежа
    if random.random() <= SUCCESS_RATE:
        # Успешный платеж
        return jsonify({
            "status": "success",
            "payment_id": f"pay_{random.randint(100000, 999999)}",
            "order_id": data['order_id'],
            "amount": data['amount'],
            "processed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }), 200
    else:
        # Неуспешный платеж
        failure_mode = random.choice(FAILURE_MODES)
        
        if failure_mode == 'timeout':
            # Имитация таймаута
            time.sleep(10)  # Долгая задержка для таймаута
            return jsonify({"error": "Payment timeout"}), 504
        elif failure_mode == 'error':
            # Имитация внутренней ошибки
            return jsonify({
                "error": "Payment processing error",
                "code": "INTERNAL_ERROR",
                "order_id": data['order_id']
            }), 500
        else:  # declined
            # Имитация отказа платежной системы
            return jsonify({
                "error": "Payment declined",
                "code": "DECLINED",
                "reason": "Insufficient funds",
                "order_id": data['order_id']
            }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004, debug=True)
