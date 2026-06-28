#!/usr/bin/env python3
"""
Загрузка всех 12 найденных кодексов в ChromaDB.
"""

from src.parsers.legal_structure_parser import LegalStructureParser
from src.converters.akoma_ntoso_converter import AkomaNtosoConverter
from src.chunking.structured_chunker import StructuredChunker
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

# Все найденные кодексы
CODES = {
    'ТК РФ': 'RusLawOD_XML/102074279.xml',
    'УК РФ': 'RusLawOD_XML/102041891.xml',
    'СК РФ': 'RusLawOD_XML/102038925.xml',
    'КАС РФ': 'RusLawOD_XML/102380990.xml',
    'ГПК РФ': 'RusLawOD_XML/102078828.xml',
    'УПК РФ': 'RusLawOD_XML/102073942.xml',
    'НК РФ': 'RusLawOD_XML/102067058.xml',
    'ВК РФ': 'RusLawOD_XML/102038209.xml',
    'ЛК РФ': 'RusLawOD_XML/102045461.xml',
    'ЖК РФ': 'RusLawOD_XML/102090645.xml',
    'КоАП РФ': 'RusLawOD_XML/102074277.xml',
    'БК РФ': 'RusLawOD_XML/102054721.xml',
}

# Инициализация компонентов
print("🔧 Инициализация компонентов...")
parser = LegalStructureParser()
converter = AkomaNtosoConverter()
chunker = StructuredChunker()
model = SentenceTransformer('intfloat/multilingual-e5-large')

# ChromaDB
client = chromadb.PersistentClient(path="./chroma_db_structured")

# Создаём или получаем коллекцию для всех кодексов
try:
    collection = client.get_collection("all_codes_structured")
    print(f"✅ Используем существующую коллекцию 'all_codes_structured' ({collection.count()} чанков)")
except:
    collection = client.create_collection(
        name="all_codes_structured",
        metadata={"hnsw:space": "cosine"}
    )
    print("✅ Создана новая коллекция 'all_codes_structured'")

# Обрабатываем каждый кодекс
total_chunks = 0
global_counter = 0
stats = {}

for code_name, file_path in CODES.items():
    print(f"\n{'='*60}")
    print(f"🔍 Обработка: {code_name} ({file_path})")
    print(f"{'='*60}")
    
    try:
        # Парсинг
        parsed_data = parser.parse_xml_file(file_path)
        heading = parsed_data['meta']['heading'] or code_name
        date = parsed_data['meta']['doc_date']
        struct_count = len(parsed_data['structure'])
        
        print(f"   ✅ Название: {heading[:80]}")
        print(f"   ✅ Дата: {date}")
        print(f"   ✅ Извлечено структурных единиц: {struct_count}")
        
        if struct_count == 0:
            print(f"   ⚠️  Нет структурных единиц, пропускаем")
            stats[code_name] = 0
            continue
        
        # Конвертация в Akoma Ntoso
        safe_name = code_name.replace(' ', '_').replace('(', '').replace(')', '')
        output_path = f'output/{safe_name}_akoma.xml'
        converter.convert(parsed_data, output_path)
        
        # Создание чанков
        chunks = chunker.create_chunks(output_path)
        print(f"   ✅ Создано {len(chunks)} чанков")
        
        if len(chunks) == 0:
            print(f"   ⚠️  Нет чанков, пропускаем")
            stats[code_name] = 0
            continue
        
        # Векторизация и загрузка
        print(f"   📦 Загрузка в ChromaDB...")
        batch_size = 100
        code_chunks = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            
            texts_to_embed = [f"{chunk['metadata']}\n{chunk['text']}" for chunk in batch]
            embeddings = model.encode(texts_to_embed)
            
            metadatas = []
            unique_ids = []
            
            for chunk in batch:
                unique_id = f"code_{safe_name}_art{global_counter}"
                global_counter += 1
                unique_ids.append(unique_id)
                
                metadata = {
                    'work_uri': str(chunk['work_uri']),
                    'expression_uri': str(chunk['expression_uri']),
                    'article_eid': str(chunk['article_eid']),
                    'article_num': str(chunk['article_num']),
                    'heading': str(chunk['heading']),
                    'metadata': str(chunk['metadata']),
                    'code_name': code_name,
                }
                
                if chunk['clause_eid'] is not None:
                    metadata['clause_eid'] = str(chunk['clause_eid'])
                else:
                    metadata['clause_eid'] = ""
                
                metadatas.append(metadata)
            
            collection.add(
                ids=unique_ids,
                embeddings=embeddings.tolist(),
                documents=[chunk['text'] for chunk in batch],
                metadatas=metadatas
            )
            
            code_chunks += len(batch)
            print(f"      ✅ Загружено {code_chunks}/{len(chunks)} чанков")
        
        total_chunks += code_chunks
        stats[code_name] = code_chunks
        
    except Exception as e:
        print(f"   ❌ Ошибка при обработке {code_name}: {e}")
        import traceback
        traceback.print_exc()
        stats[code_name] = 0
        continue

# Итоговая статистика
print(f"\n{'='*60}")
print(f"📊 СТАТИСТИКА ЗАГРУЗКИ:")
print(f"{'='*60}")

for code_name, chunks_count in stats.items():
    status = "✅" if chunks_count > 0 else "❌"
    print(f"  {status} {code_name}: {chunks_count} чанков")

print(f"\n{'='*60}")
print(f"✅ ГОТОВО! Всего загружено чанков: {collection.count()}")
print(f"{'='*60}")
