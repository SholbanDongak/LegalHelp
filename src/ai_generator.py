"""Генерация ответов через YandexGPT"""

import os
import requests
from typing import Optional

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
1. Если запрос законный — предоставь запрашиваемую информацию или сообщи, что документы прилагаются
2. Если запрос неправомерен — укажи ссылку на статью НК РФ
3. Ответ должен быть вежливым, официальным, с подписью генерального директора
""",
        "prosecutor": f"""
Ты — юридический ассистент. Составь ответ на представление прокуратуры.

{base_info}

Текст представления:
{request_text}

Требования:
1. Признай обоснованные нарушения и укажи сроки устранения
2. Если прокуратура не права — укажи основания (ст. 6 Федерального закона "О прокуратуре")
3. Ответ должен быть официальным
""",
        "court": f"""
Ты — юридический ассистент. Составь отзыв на исковое заявление или процессуальный документ.

{base_info}

Текст документа:
{request_text}

Требования:
1. Укажи позицию по каждому доводу истца
2. Ссылайся на нормы ГПК/АПК РФ
3. Если необходимо — заяви ходатайства
""",
        "counterparty": f"""
Ты — помощник руководителя. Составь ответ контрагенту.

{base_info}

Текст письма контрагента:
{request_text}

Требования:
1. Деловой, но не излишне формальный стиль
2. По существу каждого требования
3. Сохраняй партнёрский тон
""",
        "roskomnadzor": f"""
Ты — ответственный за персональные данные. Составь ответ в Роскомнадзор.

{base_info}

Текст запроса:
{request_text}

Требования:
1. Укажи, что обработка ПДн ведётся в соответствии с 152-ФЗ
2. Приложи выписку из реестра операторов
3. Ответ должен быть юридически безупречным
""",
        "fas": f"""
Ты — специалист по закупкам. Составь ответ в ФАС на жалобу.

{base_info}

Текст жалобы/запроса:
{request_text}

Требования:
1. Обоснуй правомерность действий заказчика
2. Ссылайся на 44-ФЗ или 223-ФЗ
3. Ответ должен быть чётким и аргументированным
""",
        "labor_inspection": f"""
Ты — кадровый специалист. Составь ответ в трудовую инспекцию.

{base_info}

Текст предписания/запроса:
{request_text}

Требования:
1. Подтверди устранение нарушений или обоснуй невозможность
2. Ссылайся на Трудовой кодекс РФ
3. Ответ должен содержать конкретные меры
""",
        "other": f"""
Ты — юридический ассистент. Составь официальный ответ на входящий документ.

{base_info}

Текст документа:
{request_text}

Требования:
1. Ответ должен быть вежливым и официальным
2. По существу каждого требования
3. С подписью генерального директора
"""
    }
    
    return prompts.get(document_type, prompts["other"])


def generate_answer(request_text: str, company_name: str, inn: str, document_type: str = "other") -> Optional[str]:
    """Генерирует ответ через YandexGPT"""
    
    api_key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    
    if not api_key or not folder_id:
        return "[Ошибка: не настроен YandexGPT. Добавьте YANDEX_API_KEY и YANDEX_FOLDER_ID в .env]"
    
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
