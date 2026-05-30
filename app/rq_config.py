import os
import redis
from rq import Queue

# Используем ту же переменную окружения, что и в redis_client.py
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Создаем подключение к Redis
redis_connection = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True  # Чтобы получать строки, а не байты
)

# Создаем очередь для задач (можно назвать как угодно, например 'default')
task_queue = Queue('default', connection=redis_connection)