#!/usr/bin/env python3
"""
Модуль автоматического обновления базы знаний из API pravo.gov.ru
Запуск: python update_legislation.py
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Подключаемся к ChromaDB и используем те же настройки, что в load_to_chromadb.py
try:
    import chromadb
    from chromadb.utils import embedding_functions
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что установлены chromadb, langchain-text-splitters")
    sys.exit(1)

# --- Конфигурация ---
API_BASE = "http://publication.pravo.gov.ru/api"
DAYS_BACK = 1  # Ищем документы за последние сутки
CHROMA_PATH = "./legal_chromadb"
COLLECTION_NAME = "ruslawod"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MODEL_NAME = "all-MiniLM-L6-v2"

# --- Функции для работы с API ---
def fetch_publications_by_date(date_str: str) -> Optional[List[Dict]]:
    """Получает список публикаций за указанную дату (формат ГГГГ-ММ-ДД)."""
    url = f"{API_BASE}/publications?date={date_str}"
    print(f"🔍 Запрашиваю документы за {date_str}: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        # API может возвращать список напрямую или объект с ключом 'items'
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'items' in data:
            return data['items']
        else:
            print(f"⚠️ Неизвестный формат ответа: {type(data)}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе к API: {e}")
        return None

def fetch_document_text(doc_id: str) -> Optional[str]:
    """Загружает полный текст документа по его ID (nd)."""
    # Эндпоинт может отличаться, проверяем два варианта
    url1 = f"{API_BASE}/publication/{doc_id}"
    url2 = f"{API_BASE}/documents/{doc_id}"
    for url in (url1, url2):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                # Пытаемся извлечь текст из разных возможных полей
                text = data.get('fullText') or data.get('text') or data.get('content')
                if text:
                    return text
        except:
            continue
    print(f"⚠️ Не удалось загрузить текст документа {doc_id}")
    return None

# --- Функции для работы с ChromaDB ---
def get_chroma_collection():
    """Подключается к ChromaDB и возвращает коллекцию."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    try:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"✅ Подключено к коллекции '{COLLECTION_NAME}'")
    except:
        print(f"❌ Коллекция '{COLLECTION_NAME}' не найдена. Сначала запустите load_to_chromadb.py")
        sys.exit(1)
    return collection

def document_exists(collection, doc_id: str) -> bool:
    """Проверяет, есть ли уже документ в базе (по ID)."""
    try:
        result = collection.get(where={"source": doc_id}, limit=1)
        return len(result['ids']) > 0
    except:
        return False

def add_document_to_chromadb(collection, doc_id: str, text: str):
    """Разбивает текст на чанки и добавляет в ChromaDB."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
        length_function=len
    )
    chunks = splitter.split_text(text)
    if not chunks:
        print(f"⚠️ Текст документа {doc_id} пустой или слишком короткий")
        return 0
    for idx, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{idx}"
        collection.add(
            ids=[chunk_id],
            documents=[chunk],
            metadatas=[{"source": doc_id, "filename": f"{doc_id}.xml"}]
        )
    print(f"📄 Добавлен документ {doc_id} ({len(chunks)} чанков)")
    return len(chunks)

# --- Основная функция обновления ---
def update_knowledge_base():
    print("--- Запуск ежедневного обновления базы знаний ---")
    print(f"Дата запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Подключаемся к ChromaDB
    collection = get_chroma_collection()
    
    # 2. Определяем дату поиска (за последние DAYS_BACK дней)
    target_date = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")
    
    # 3. Получаем список публикаций
    publications = fetch_publications_by_date(target_date)
    if not publications:
        print("⚠️ Нет публикаций или ошибка получения. Завершаю.")
        return
    
    print(f"📑 Получено {len(publications)} публикаций за {target_date}")
    
    new_count = 0
    for pub in publications:
        # У разных документов ID может называться по-разному
        doc_id = pub.get('nd') or pub.get('id') or pub.get('number')
        if not doc_id:
            continue
        
        # Пропускаем уже существующие
        if document_exists(collection, doc_id):
            print(f"⏩ Документ {doc_id} уже в базе, пропускаю")
            continue
        
        # Загружаем полный текст
        text = fetch_document_text(doc_id)
        if not text:
            continue
        
        # Добавляем в ChromaDB
        chunks_added = add_document_to_chromadb(collection, doc_id, text)
        if chunks_added:
            new_count += 1
    
    print(f"--- Обновление завершено. Добавлено новых документов: {new_count} ---")

if __name__ == "__main__":
    update_knowledge_base()