#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для автоматического обновления базы законов из API pravo.gov.ru
Адаптирован под новый эндпоинт /api/Documents (июнь 2026)
Фильтрует только федеральные законы (eoNumber начинается с '000120')
"""

import os
import sys
import requests
import json
import time
import hashlib
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import logging
from tqdm import tqdm

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
CHROMA_PATH = "./legal_chromadb"
XML_FOLDER = "./RusLawOD_XML"
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "ruslawod"
API_BASE = "http://publication.pravo.gov.ru/api/Documents"
PAGE_SIZE = 100  # количество документов на страницу

# Инициализация модели эмбеддингов
logger.info("Загрузка модели эмбеддингов...")
model = SentenceTransformer(MODEL_NAME)

# Подключение к ChromaDB
logger.info("Подключение к ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    collection = client.get_collection(COLLECTION_NAME)
except:
    logger.error("Коллекция 'ruslawod' не найдена. Сначала запустите load_to_chromadb.py")
    sys.exit(1)

def get_documents_for_date(date_str):
    """Получить список документов за указанную дату через API"""
    all_items = []
    page = 1
    total_pages = 1
    
    while page <= total_pages:
        url = f"{API_BASE}?PeriodType=day&Date={date_str}&PageSize={PAGE_SIZE}&Index={page}"
        logger.info(f"Запрос страницы {page}: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Ошибка API: {response.status_code} - {response.text[:200]}")
                break
            
            data = response.json()
            items = data.get('items', [])
            if not items:
                break
                
            all_items.extend(items)
            
            # Обновляем информацию о страницах
            total_pages = data.get('pagesTotalCount', 1)
            logger.info(f"Получено {len(items)} документов, всего страниц: {total_pages}")
            
            if page >= total_pages:
                break
                
            page += 1
            time.sleep(0.5)  # небольшая пауза между запросами
            
        except Exception as e:
            logger.error(f"Ошибка при запросе: {e}")
            break
    
    return all_items

def download_document_xml(doc_id, doc_number, save_path):
    """Скачать XML-файл документа по ID"""
    # Пробуем разные варианты эндпоинтов для скачивания
    endpoints = [
        f"{API_BASE}/{doc_id}/xml",
        f"{API_BASE}/{doc_id}/file?format=xml",
        f"{API_BASE}/{doc_id}?format=xml"
    ]
    
    for url in endpoints:
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200 and response.content:
                # Проверяем, что это действительно XML (начинается с '<')
                content_preview = response.content[:100].decode('utf-8', errors='ignore')
                if content_preview.strip().startswith('<'):
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Скачан: {doc_number} -> {os.path.basename(save_path)}")
                    return True
        except Exception as e:
            logger.warning(f"Ошибка скачивания через {url}: {e}")
            continue
    
    logger.warning(f"Не удалось скачать {doc_number} (ID: {doc_id})")
    return False

def process_document(doc):
    """Обработка одного документа: скачивание и добавление в ChromaDB"""
    doc_id = doc.get('id')
    eo_number = doc.get('eoNumber')
    title = doc.get('title', '')
    
    if not doc_id or not eo_number:
        return False

    # --- ФИЛЬТР: только федеральные законы (префикс 000120) ---
    if not eo_number.startswith('000120'):
        logger.debug(f"Пропускаем {eo_number} (не федеральный закон)")
        return False
    # ---------------------------------------------------------
    
    # Проверяем, не скачан ли уже этот документ
    filename = f"{eo_number}.xml"
    filepath = os.path.join(XML_FOLDER, filename)
    
    if os.path.exists(filepath):
        logger.debug(f"Документ {eo_number} уже существует, пропускаем")
        return False
    
    # Скачиваем XML
    os.makedirs(XML_FOLDER, exist_ok=True)
    if not download_document_xml(doc_id, eo_number, filepath):
        return False
    
    # Теперь добавим в ChromaDB
    try:
        add_to_chromadb(filepath)
        logger.info(f"Добавлен в базу: {eo_number}")
        return True
    except Exception as e:
        logger.error(f"Ошибка добавления {eo_number}: {e}")
        os.remove(filepath)  # удаляем битый файл
        return False

def add_to_chromadb(filepath):
    """Разбить XML на чанки и добавить в ChromaDB"""
    # читаем XML
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        # Извлекаем весь текст из XML
        text_parts = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_parts.append(elem.text.strip())
            if elem.tail and elem.tail.strip():
                text_parts.append(elem.tail.strip())
        full_text = ' '.join(text_parts)
        if not full_text.strip():
            raise ValueError("Пустой текст")
    except Exception as e:
        logger.error(f"Ошибка парсинга XML {filepath}: {e}")
        raise

    # Разбиваем на чанки (простой способ — по абзацам или по длине)
    # Здесь можно использовать ваш метод из load_to_chromadb.py
    # Для примера — разбиваем по предложениям (упрощённо)
    chunks = []
    sentences = full_text.split('. ')
    current_chunk = ""
    for sent in sentences:
        if len(current_chunk) + len(sent) < 500:
            current_chunk += sent + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sent + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())

    if not chunks:
        chunks = [full_text[:1000]]  # если не удалось разбить, берём первые 1000 символов

    # Вычисляем эмбеддинги
    embeddings = model.encode(chunks, convert_to_numpy=True)

    # Генерируем ID для чанков
    file_id = os.path.basename(filepath).replace('.xml', '')
    ids = [f"{file_id}_{i}" for i in range(len(chunks))]

    # Добавляем в коллекцию
    collection.add(
        embeddings=embeddings.tolist(),
        documents=chunks,
        ids=ids,
        metadatas=[{"source": os.path.basename(filepath)} for _ in chunks]
    )
    logger.info(f"Добавлено {len(chunks)} чанков из {os.path.basename(filepath)}")

def main():
    # Определяем дату: либо переданный параметр, либо вчерашний день
    if len(sys.argv) > 1:
        try:
            date_str = sys.argv[1]
            datetime.strptime(date_str, "%Y-%m-%d")
        except:
            logger.error("Неверный формат даты. Используйте YYYY-MM-DD")
            sys.exit(1)
    else:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    logger.info(f"Обновление законодательства за дату: {date_str}")

    # Получаем список документов
    docs = get_documents_for_date(date_str)
    logger.info(f"Найдено документов: {len(docs)}")

    if not docs:
        logger.info("Нет новых документов")
        return

    # Обрабатываем документы
    added = 0
    for doc in tqdm(docs, desc="Обработка документов"):
        if process_document(doc):
            added += 1

    logger.info(f"Обновление завершено. Добавлено {added} новых документов.")

if __name__ == "__main__":
    main()