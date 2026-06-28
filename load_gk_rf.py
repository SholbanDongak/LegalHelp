#!/usr/bin/env python3
"""
Загрузка всех 4 частей Гражданского кодекса РФ в ChromaDB.
"""

from src.parsers.legal_structure_parser import LegalStructureParser
from src.converters.akoma_ntoso_converter import AkomaNtosoConverter
from src.chunking.structured_chunker import StructuredChunker
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

# Файлы всех 4 частей ГК РФ
GK_RF_FILES = {
    'part1': 'RusLawOD_XML/102033239.xml',
    'part2': 'RusLawOD_XML/102039276.xml',
    'part3': 'RusLawOD_XML/102073578.xml',
    'part4': 'RusLawOD_XML/102110716.xml'
}

# Инициализация компонентов
parser = LegalStructureParser()
converter = AkomaNtosoConverter()
chunker = StructuredChunker()
model = SentenceTransformer('intfloat/multilingual-e5-large')

# ChromaDB
client = chromadb.PersistentClient(path="./chroma_db_structured")

# Создаём или получаем коллекцию для ГК РФ
try:
    collection = client.get_collection("gk_rf_structured")
    print("✅ Используем существующую коллекцию 'gk_rf_structured'")
except:
    collection = client.create_collection(
        name="gk_rf_structured",
        metadata={"hnsw:space": "cosine"}
    )
    print("✅ Создана новая коллекция 'gk_rf_structured'")

# Обрабатываем каждую часть ГК РФ
total_chunks = 0
global_counter = 0

for part_name, file_path in GK_RF_FILES.items():
    print(f"\n{'='*60}")
    print(f"🔍 Обработка: {part_name} ({file_path})")
    print(f"{'='*60}")
    
    try:
        # Парсинг
        parsed_data = parser.parse_xml_file(file_path)
        print(f"   ✅ Название: {parsed_data['meta']['heading']}")
        print(f"   ✅ Дата: {parsed_data['meta']['doc_date']}")
        print(f"   ✅ Извлечено структурных единиц: {len(parsed_data['structure'])}")
        
        if len(parsed_data['structure']) == 0:
            print(f"   ⚠️  Нет структурных единиц, пропускаем")
            continue
        
        # Конвертация в Akoma Ntoso
        output_path = f'output/gk_rf_{part_name}_akoma.xml'
        converter.convert(parsed_data, output_path)
        
        # Создание чанков
        chunks = chunker.create_chunks(output_path)
        print(f"   ✅ Создано {len(chunks)} чанков")
        
        if len(chunks) == 0:
            print(f"   ⚠️  Нет чанков, пропускаем")
            continue
        
        # Векторизация и загрузка
        print(f"   📦 Загрузка в ChromaDB...")
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            
            # Векторизуем текст + метаданные
            texts_to_embed = [f"{chunk['metadata']}\n{chunk['text']}" for chunk in batch]
            embeddings = model.encode(texts_to_embed)
            
            # Формируем метаданные и уникальные ID
            metadatas = []
            unique_ids = []
            
            for chunk in batch:
                unique_id = f"gk_{part_name}_art{global_counter}"
                global_counter += 1
                unique_ids.append(unique_id)
                
                metadata = {
                    'work_uri': str(chunk['work_uri']),
                    'expression_uri': str(chunk['expression_uri']),
                    'article_eid': str(chunk['article_eid']),
                    'article_num': str(chunk['article_num']),
                    'heading': str(chunk['heading']),
                    'metadata': str(chunk['metadata']),
                    'part_name': part_name,
                    'code_type': 'ГК РФ'
                }
                
                if chunk['clause_eid'] is not None:
                    metadata['clause_eid'] = str(chunk['clause_eid'])
                else:
                    metadata['clause_eid'] = ""
                
                metadatas.append(metadata)
            
            # Добавляем в БД
            collection.add(
                ids=unique_ids,
                embeddings=embeddings.tolist(),
                documents=[chunk['text'] for chunk in batch],
                metadatas=metadatas
            )
            
            total_chunks += len(batch)
            print(f"      ✅ Загружено {total_chunks} чанков")
        
    except Exception as e:
        print(f"   ❌ Ошибка при обработке {part_name}: {e}")
        import traceback
        traceback.print_exc()
        continue

print(f"\n{'='*60}")
print(f"✅ ГОТОВО! Всего загружено чанков: {collection.count()}")
print(f"{'='*60}")
