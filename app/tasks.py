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
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        return asyncio.create_task(coro)
    else:
        return asyncio.run(coro)


@celery_app.task(
    bind=True,
    name="send_welcome_email",
    max_retries=3,
    default_retry_delay=60,
    rate_limit="10/m",
)
def send_welcome_email(self, user_id: int):

    logger.info(f"Starting send_welcome_email for user_id={user_id}")

    try:
        user = get_user_by_id_sync(user_id)

        if not user:
            logger.error(f"User {user_id} not found")
            raise ValueError(f"User {user_id} not found")

        import time
        time.sleep(5)

        logger.info(f"Welcome email sent to {user.login} (user_id={user_id})")
        return f"Email sent to {user.login}"
    except Exception as e:
        logger.exception(f"Failed to send welcome email for user {user_id}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)