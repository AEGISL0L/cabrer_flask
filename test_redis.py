import redis

try:
    r = redis.Redis(host='127.0.0.1', port=6379)
    print(r.ping())  # Debería imprimir 'True'
except Exception as e:
    print("Error conectando a Redis:", e)

