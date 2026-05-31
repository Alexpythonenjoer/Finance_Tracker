from app.ai_client import get_openrouter_client


ALLOWED_CATEGORIES = [
    "Еда", "Транспорт", "Развлечения", "Здоровье",
    "Дом", "Зарплата", "Переводы", "Другое"
]


async def suggest_category(description: str) -> str | None:
    if not description or len(description.strip()) == 0:
        return None

    client = get_openrouter_client()

    categories_str = ", ".join(ALLOWED_CATEGORIES)
    prompt = f"""
Ты — финансовый ассистент. Проанализируй описание траты: "{description}".
Определи, к какой из следующих категорий она относится: {categories_str}.
Если описание не подходит ни под одну категорию, ответь "Другое".
Верни ТОЛЬКО название категории, без лишних слов, кавычек и точек.
"""
    try:

        response = await client.chat.send_async(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )

        category = response.choices[0].message.content.strip()
        if category in ALLOWED_CATEGORIES:
            return category
        return "Другое"
    except Exception as e:

        print(f"OpenRouter API error: {e}")
        return None