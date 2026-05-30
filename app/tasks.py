import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from app.repository.users import get_user_by_id_sync
from app.celery_app import celery_app
from app.repository import users as users_repository
from app.repository import wallets as wallets_repository
from app.repository import operations as operations_repository
from app.service.exchenge_service import get_exchange_rate

logger = logging.getLogger(__name__)

def run_async(coro):
    """Вспомогательная функция для выполнения асинхронного кода в синхронной Celery-задаче."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Если цикл уже запущен (например, в тестах), создаём новую задачу
        return asyncio.create_task(coro)
    else:
        # Обычный случай: запускаем цикл до завершения
        return asyncio.run(coro)


@celery_app.task(
    bind=True,
    name="send_welcome_email",
    max_retries=3,
    default_retry_delay=60,
    rate_limit="10/m",
)
def send_welcome_email(self, user_id: int):
    """
    Отправляет приветственное письмо пользователю (симуляция).
    В реальности здесь был бы вызов SMTP или внешнего API.
    """
    logger.info(f"Starting send_welcome_email for user_id={user_id}")

    try:
        # Асинхронный вызов репозитория
        user = get_user_by_id_sync(user_id)
        # ВАЖНО: в run_async нужно передать сессию. Для простоты здесь опущено,
        # Для демонстрации пока заменим на заглушку:
        # Правильнее будет создать отдельную синхронную функцию в репозитории,
        # либо передавать сессию через аргументы задачи.
        # Упростим: будем считать, что user найден.
        if not user:
            logger.error(f"User {user_id} not found")
            raise ValueError(f"User {user_id} not found")

        # Симуляция долгой операции (отправка письма)
        import time
        time.sleep(5)

        logger.info(f"Welcome email sent to {user.login} (user_id={user_id})")
        return f"Email sent to {user.login}"
    except Exception as e:
        logger.exception(f"Failed to send welcome email for user {user_id}")
        # Повторяем задачу с экспоненциальной задержкой
        raise self.retry(exc=e, countdown=2 ** self.request.retries)