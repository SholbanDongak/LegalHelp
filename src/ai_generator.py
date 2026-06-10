import asyncio
import json
import os
from ollama import AsyncClient

MODEL_NAME = "qwen2.5:7b-instruct"
TEMPLATES_DIR = "./templates"

def load_template(subtype: str) -> str:
    path = os.path.join(TEMPLATES_DIR, f"{subtype}.txt")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def fill_template(template: str, data: dict) -> str:
    for key, value in data.items():
        if value:
            template = template.replace(f"[{key}]", str(value))
    return template

async def generate_answer_async(query: str, company_name: str, inn: str, doc_type: str = "other") -> str:
    client = AsyncClient(host='http://127.0.0.1:11434')
    
    if doc_type == "judicial_review":
        try:
            data = json.loads(query)
            subtype = data.get("subtype")
            if not subtype:
                return "Не указан тип документа"
            template = load_template(subtype)
            if not template:
                return f"Шаблон для '{subtype}' не найден"
            filled = fill_template(template, data)
            prompt = f"Ты – юридический ассистент. На основе приведённого ниже шаблона составь итоговый документ в официально-деловом стиле. Замени все [плейсхолдеры] на конкретные значения из данных. Если каких-то данных нет, оставь плейсхолдер или предложи ввести.\n\n{filled}"
            response = await client.chat(model=MODEL_NAME, messages=[
                {"role": "system", "content": "Ты – опытный юрист. Составляешь документы строго по шаблону, сохраняя структуру и официальный стиль."},
                {"role": "user", "content": prompt}
            ])
            return response['message']['content']
        except Exception as e:
            return f"Ошибка при генерации документа: {e}"
    else:
        response = await client.chat(model=MODEL_NAME, messages=[
            {"role": "system", "content": "Ты – юридический консультант. Отвечай на вопросы пользователя на русском языке, ссылаясь на законы РФ. Если не знаешь точного ответа, скажи, что нужно проконсультироваться с юристом."},
            {"role": "user", "content": query}
        ])
        return response['message']['content']

def generate_answer(query: str, company_name: str, inn: str, doc_type: str = "other") -> str:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Нет запущенного цикла, можно использовать asyncio.run
        return asyncio.run(generate_answer_async(query, company_name, inn, doc_type))
    else:
        # Цикл уже запущен (uvicorn), нужно создать новую задачу и дождаться
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, generate_answer_async(query, company_name, inn, doc_type))
            return future.result()