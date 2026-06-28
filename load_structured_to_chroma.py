from src.parsers.legal_structure_parser import LegalStructureParser
from src.converters.akoma_ntoso_converter import AkomaNtosoConverter
from src.chunking.structured_chunker import StructuredChunker
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

# Инициализация
parser = LegalStructureParser()
converter = AkomaNtosoConverter()
chunker = StructuredChunker()
model = SentenceTransformer('intfloat/multilingual-e5-large')

# ChromaDB
client = chromadb.PersistentClient(path="./chroma_db_structured")

# Удаляем старую коллекцию
try:
    client.delete_collection("legal_corpus_structured")
except:
    pass

collection = client.create_collection(
    name="legal_corpus_structured",
    metadata={"hnsw:space": "cosine"}
)

# Обрабатываем Конституцию
print("🔍 Обработка Конституции РФ...")
parsed_data = parser.parse_xml_file('RusLawOD_XML/102027595.xml')
converter.convert(parsed_data, 'output/constitution_akoma.xml')
chunks = chunker.create_chunks('output/constitution_akoma.xml')

# ИСПРАВЛЕНИЕ: Делаем ID уникальными, добавляя глобальный счетчик
print(f"📦 Загрузка {len(chunks)} чанков в ChromaDB...")
batch_size = 100
global_counter = 0

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    
    # Векторизуем текст + метаданные
    texts_to_embed = [f"{chunk['metadata']}\n{chunk['text']}" for chunk in batch]
    embeddings = model.encode(texts_to_embed)
    
    # Формируем метаданные и уникальные ID
    metadatas = []
    unique_ids = []
    
    for chunk in batch:
        # Уникальный ID с глобальным счетчиком
        unique_id = f"const_art{global_counter}"
        global_counter += 1
        unique_ids.append(unique_id)
        
        metadata = {
            'work_uri': str(chunk['work_uri']),
            'expression_uri': str(chunk['expression_uri']),
            'article_eid': str(chunk['article_eid']),
            'article_num': str(chunk['article_num']),
            'heading': str(chunk['heading']),
            'metadata': str(chunk['metadata'])
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
    
    print(f"  ✅ Загружено {i+len(batch)} чанков")

print(f"\n✅ ГОТОВО! Всего чанков: {collection.count()}")
