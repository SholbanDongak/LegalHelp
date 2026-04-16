"""Генерация ответов через YandexGPT"""

import os
import requests


def get_prompt(document_type: str, request_text: str, company_name: str, inn: str) -> str:
    """Возвращает промпт в зависимости от типа документа"""

    base_info = f"Компания: {company_name}, ИНН: {inn}"

    prompts = {
        "fns": f"""
Ты — юридический ассистент. Составь официальный ответ на запрос налоговой инспекции.

{base_info}

Текст запроса ФНС:
{request_text}

Требования к ответу:
1. Если запрос законный — предоставь запрашиваемую информацию
2. Если запрос неправомерен — укажи ссылку на статью НК РФ
3. Ответ должен быть вежливым, официальным
""",
        "court": f"""
Ты — юридический ассистент. Составь отзыв на исковое заявление.

{base_info}

Текст документа:
{request_text}

Требования:
1. Укажи позицию по каждому доводу истца
2. Ссылайся на нормы ГПК/АПК РФ
""",
        "counterparty": f"""
Ты — помощник руководителя. Составь ответ контрагенту.

{base_info}

Текст письма контрагента:
{request_text}

Требования:
1. Деловой, но не излишне формальный стиль
2. По существу каждого требования
""",
        "other": f"""
Ты — юридический ассистент. Составь официальный ответ на входящий документ.

{base_info}

Текст документа:
{request_text}

Требования:
1. Ответ должен быть вежливым и официальным
2. По существу каждого требования
"""
    }

    return prompts.get(document_type, prompts["other"])


def generate_answer(request_text: str, company_name: str, inn: str, document_type: str = "other") -> str:
    """Генерирует ответ через YandexGPT"""

    api_key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")

    if not api_key or not folder_id or api_key == "test_key":
        prompt = get_prompt(document_type, request_text, company_name, inn)
        return f"[ТЕСТОВЫЙ РЕЖИМ] YandexGPT не настроен.\n\nСгенерированный промпт:\n{prompt[:500]}..."

    prompt = get_prompt(document_type, request_text, company_name, inn)

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "temperature": 0.3,
            "maxTokens": 2000
        },
        "messages": [
            {"role": "system", "text": "Ты — юридический ассистент. Составляй официальные ответы на русском языке."},
            {"role": "user", "text": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        result = response.json()
        return result["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        return f"[Ошибка генерации: {str(e)}]"
