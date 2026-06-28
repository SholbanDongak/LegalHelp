import asyncio
import json
import os
import re
from ollama import AsyncClient
from src.unified_retriever import UnifiedRetriever
from src.verification.citation_verifier import CitationVerifier

MODEL_NAME = "llama3.1:8b"
TEMPLATES_DIR = "./templates"

print("🔍 Инициализация UnifiedRetriever...")
try:
    retriever = UnifiedRetriever()
    
    # Получаем список доступных статей для верификации
    all_articles = set()
    for code_name, collection in retriever.collections.items():
        results = collection.get()
        for metadata in results['metadatas']:
            match = re.search(r'(\d+)', metadata.get('article_num', ''))
            if match:
                all_articles.add(match.group(1))
    
    verifier = CitationVerifier(all_articles)
    print(f"✅ UnifiedRetriever инициализирован. Модель: {MODEL_NAME}")
    print(f"✅ Всего статей в базе: {len(all_articles)}")
except Exception as e:
    print(f"⚠️  Ошибка инициализации retriever: {e}")
    retriever = None
    verifier = None

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

async def generate_answer_with_rag(query: str, company_name: str, inn: str, doc_type: str = "other") -> str:
    """Генерирует ответ с использованием RAG по всем кодексам."""
    client = AsyncClient(host='http://127.0.0.1:11434')
    
    context = ""
    sources = []
    
    if retriever:
        try:
            context, sources = retriever.query(query, top_k=5)
            print(f"🔍 Найдено {len(sources)} релевантных статей")
        except Exception as e:
            print(f"⚠️  Ошибка поиска: {e}")
            context = ""
            sources = []
    
    if context:
        system_prompt = f"""Ты — юридический консультант, специалист по праву Российской Федерации.

Отвечай строго на русском языке в официально-деловом стиле.

ПРАВИЛА:
1. Используй ТОЛЬКО информацию из предоставленного контекста (Конституция РФ, ГК РФ, другие кодексы).
2. Цитируй статьи и пункты точно, указывая их номера и кодекс (например, "согласно статье 454 ГК РФ, пункту 1").
3. Если в контексте нет ответа, прямо скажи: "В предоставленных правовых актах нет информации по данному вопросу."
4. Не придумывай статьи или нормы, которых нет в контексте.
5. Не добавляй список источников в конце ответа.

КОНТЕКСТ ИЗ ПРАВОВЫХ АКТОВ:
{context}"""
    else:
        system_prompt = """Ты — юридический консультант. Отвечай на русском языке в официально-деловом стиле.
Если не знаешь точного ответа, честно скажи, что нужно проконсультироваться с юристом."""
    
    user_prompt = query
    
    try:
        response = await client.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 1024
            }
        )
        answer = response['message']['content']
        
        # Верификация цитат
        if verifier:
            is_valid, errors = verifier.verify(answer)
            if not is_valid:
                warning = "\n\n⚠️ ВНИМАНИЕ: Некоторые упомянутые статьи не найдены в базе:\n"
                warning += "\n".join(f"  - {error}" for error in errors)
                warning += "\nПожалуйста, проверьте информацию в официальных источниках."
                answer += warning
        
        # Добавляем источники
        no_info_phrases = ["нет информации", "не содержится", "не регулируется", "не указано", "отсутствует"]
        has_no_info = any(phrase in answer.lower() for phrase in no_info_phrases)
        
        answer_without_sources = re.sub(r'📚 Источники:.*$', '', answer, flags=re.DOTALL).strip()
        is_short_no_info = len(answer_without_sources) < 200 and has_no_info
        
        if sources and not is_short_no_info:
            unique_sources = []
            seen = set()
            for source in sources:
                source_key = f"{source['code_display']}_{source['article_num']}"
                if source_key not in seen:
                    unique_sources.append(source)
                    seen.add(source_key)
            
            answer += "\n\n📚 Источники:\n"
            for source in unique_sources:
                answer += f"  - [{source['code_display']}] {source['metadata']}\n"
        
        return answer
        
    except Exception as e:
        print(f"❌ Ошибка при генерации ответа: {e}")
        return f"Ошибка при генерации ответа: {e}"

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
            prompt = f"Составь юридический документ в официально-деловом стиле на русском языке по шаблону. Замени плейсхолдеры на конкретные значения.\n\n{filled}"
            response = await client.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Ты — опытный юрист. Отвечай только на русском языке. Строго следуй шаблону."},
                    {"role": "user", "content": prompt}
                ],
                options={"temperature": 0.1}
            )
            return response['message']['content']
        except Exception as e:
            return f"Ошибка при генерации документа: {e}"
    else:
        return await generate_answer_with_rag(query, company_name, inn, doc_type)

def generate_answer(query: str, company_name: str, inn: str, doc_type: str = "other") -> str:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(generate_answer_async(query, company_name, inn, doc_type))
    else:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, generate_answer_async(query, company_name, inn, doc_type))
            return future.result()
