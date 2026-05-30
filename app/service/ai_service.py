from app.ai_client import get_openrouter_client

# Доступные категории (можно вынести в конфиг)
ALLOWED_CATEGORIES = [
    "Еда", "Транспорт", "Развлечения", "Здоровье",
    "Дом", "Зарплата", "Переводы", "Другое"
]


async def suggest_category(description: str) -> str | None:
    """
    Отправляет описание транзакции в OpenRouter API и возвращает предложенную категорию.
    При ошибке возвращает None.
    """
    if not description or len(description.strip()) == 0:
        return None

    client = get_openrouter_client()

    # Формируем промпт
    categories_str = ", ".join(ALLOWED_CATEGORIES)
    prompt = f"""
Ты — финансовый ассистент. Проанализируй описание траты: "{description}".
Определи, к какой из следующих категорий она относится: {categories_str}.
Если описание не подходит ни под одну категорию, ответь "Другое".
Верни ТОЛЬКО название категории, без лишних слов, кавычек и точек.
"""
    try:
        # Асинхронный вызов API через SDK
        response = await client.chat.send_async(
            model="openai/gpt-4o-mini",  # дешёвая и быстрая модель
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # детерминированные ответы
            max_tokens=10
        )

        category = response.choices[0].message.content.strip()
        # Проверяем, что категория входит в список
        if category in ALLOWED_CATEGORIES:
            return category
        return "Другое"
    except Exception as e:
        # В вашем проекте можно использовать logger
        print(f"OpenRouter API error: {e}")
        return None