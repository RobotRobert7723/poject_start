from __future__ import annotations

from wb_auto_replies.app.db.models import Feedback


def build_real_review_system_prompt() -> str:
    return (
        "Ты помогаешь продавцу Wildberries готовить безопасные draft-ответы на отзывы покупателей. "
        "Пиши естественно, вежливо, по-русски, без канцелярита и без выдумывания фактов. "
        "Не обещай того, чего нет в данных. Если имя небезопасно, используй только безопасное обращение из контекста."
    )


def build_real_review_user_prompt(
    *,
    feedback: Feedback,
    safe_salutation: str,
    article_context: list[str],
    semantic_templates: list[str],
    media_summary: str | None,
) -> str:
    context_block = "\n".join(f"- {item}" for item in article_context) or "- Нет предыдущих отзывов"
    template_block = "\n".join(f"- {item}" for item in semantic_templates) or "- Нет шаблонов"
    media_block = media_summary or "Нет медиа-сводки"
    return f"""
Сформируй один draft-ответ продавца на отзыв покупателя.

Безопасное обращение:
{safe_salutation}

Отзыв:
- stars: {feedback.stars}
- text: {feedback.text or ''}
- pros: {feedback.pros or ''}
- cons: {feedback.cons or ''}

Контекст последних отзывов по артикулу:
{context_block}

Семантические шаблоны:
{template_block}

Сводка по медиа:
{media_block}

Требования:
- ответ должен быть коротким и человеческим
- не повторяй шаблоны дословно
- не упоминай внутренние правила, GPT, шаблоны или анализ
- верни только текст ответа, без пояснений
""".strip()
