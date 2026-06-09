import asyncio
import json
import re
import os
from ollama import AsyncClient
from src.retriever import LawRetriever
from src.judicial_prompts import get_judicial_prompt

MODEL_NAME = "qwen2.5:7b-instruct"
retriever = LawRetriever()
TEMPLATES_DIR = "./templates"

SYSTEM_PROMPT = """Ты — юридический ассистент. Отвечай только на основе предоставленного контекста.
Если ответа нет в контексте, скажи: "Информация не найдена".
Всегда ссылайся на источник (ID документа). Используй официально-деловой стиль."""

def clean_and_parse_json(raw_query: str) -> dict:
    if not raw_query:
        return {}
    cleaned = re.sub(r'[\x00-\x1f\x7f]', '', raw_query)
    cleaned = re.sub(r'(\d{1,2}\.\d{1,2}),(\d{4})', r'\1.\2', cleaned)
    try:
        data = json.loads(cleaned)
        return {k: v for k, v in data.items() if v and str(v).strip()}
    except json.JSONDecodeError:
        return {}

def load_template_from_file(subtype: str) -> str:
    filepath = os.path.join(TEMPLATES_DIR, f"{subtype}.txt")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

async def generate_answer_async(query: str, company_name: str, inn: str, doc_type: str = "other") -> str:
    # Судебные документы
    if doc_type == "judicial_review":
        data = clean_and_parse_json(query)
        subtype = data.get("subtype", "unknown")
        template_text = load_template_from_file(subtype)
        if not template_text:
            return f"⚠️ Шаблон для типа '{subtype}' не найден. Проверьте файл {subtype}.txt в папке templates."
        contexts, sources = retriever.retrieve(query)
        prompt = get_judicial_prompt(doc_type, data, "\n".join(contexts) if contexts else "Законы не найдены.", template_text)
        client = AsyncClient(host='http://127.0.0.1:11434')
        response = await client.chat(model=MODEL_NAME, messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        return response['message']['content']
    
    # Общие вопросы (демо-режим, чтобы избежать ошибки 400)
    return f"✅ Демо-ответ на вопрос: {query[:200]}... (Полноценный RAG заработает после загрузки всех законов)"

def generate_answer(query: str, company_name: str, inn: str, doc_type: str = "other") -> str:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, generate_answer_async(query, company_name, inn, doc_type))
            return future.result()
    else:
        return asyncio.run(generate_answer_async(query, company_name, inn, doc_type))
