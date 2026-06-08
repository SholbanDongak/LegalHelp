import os
import asyncio
from ollama import AsyncClient

MODEL_NAME = "qwen2.5:7b-instruct"

SYSTEM_PROMPT = """Ты — опытный юридический ассистент. Твоя задача — генерировать юридически корректные и грамотные черновики ответов на официальные запросы (ФНС, суд, прокуратура и т.д.).
Пиши на русском языке, используй официально-деловой стиль. Всегда опирайся на нормы законодательства РФ. Если ответа не знаешь — так и скажи, не выдумывай факты."""

def get_prompt(document_type: str, request_text: str, company_name: str, inn: str) -> str:
    base_info = f"Компания: {company_name}, ИНН: {inn}"
    prompts = {
        "fns": f"""Составь официальный ответ на запрос налоговой инспекции.
Информация о компании: {base_info}
Текст запроса ФНС: {request_text}
Требования:
1. Если запрос законный — предоставь запрашиваемую информацию.
2. Если запрос неправомерен — укажи ссылку на статью НК РФ.
3. Ответ должен быть вежливым, официальным.""",
        "court": f"""Составь отзыв на исковое заявление.
Информация о компании: {base_info}
Текст документа: {request_text}
Требования:
1. Укажи позицию по каждому доводу истца.
2. Ссылайся на нормы ГПК/АПК РФ.""",
        "counterparty": f"""Составь ответ контрагенту.
Информация о компании: {base_info}
Текст письма контрагента: {request_text}
Требования:
1. Деловой, но не излишне формальный стиль.
2. Ответь по существу каждого требования.""",
        "other": f"""Составь официальный ответ на входящий документ.
Информация о компании: {base_info}
Текст документа: {request_text}
Требования:
1. Ответ должен быть вежливым и официальным.
2. Ответь по существу каждого требования."""
    }
    return prompts.get(document_type, prompts["other"])

async def generate_answer_async(request_text: str, company_name: str, inn: str, document_type: str = "other") -> str:
    try:
        prompt = get_prompt(document_type, request_text, company_name, inn)
        client = AsyncClient()
        response = await client.chat(model=MODEL_NAME, messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        return response['message']['content']
    except Exception as e:
        print(f"Ошибка при генерации ответа: {e}")
        return f"[Ошибка генерации: Убедитесь, что Ollama запущен (ollama serve) и модель '{MODEL_NAME}' загружена.]"

def generate_answer(request_text: str, company_name: str, inn: str, document_type: str = "other") -> str:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, generate_answer_async(request_text, company_name, inn, document_type))
            return future.result()
    else:
        return asyncio.run(generate_answer_async(request_text, company_name, inn, document_type))
