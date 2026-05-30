def send_welcome_email(username: str):
    """
    Фоновая задача для имитации отправки приветственного сообщения.
    """
    import time
    import logging
    from datetime import datetime

    logger = logging.getLogger(__name__)
    logger.info(f"Starting welcome task for {username}")
    time.sleep(5)  # симулируем долгую операцию
    logger.info(f"Welcome message sent to {username} at {datetime.now()}")
    return f"Task for {username} completed"