import os
import xml.etree.ElementTree as ET
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

XML_DIR = "./RusLawOD_XML"
CHROMA_PATH = "./legal_chromadb"
COLLECTION_NAME = "ruslawod"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MODEL_NAME = "all-MiniLM-L6-v2"

print("Подключение к ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)

# НЕ УДАЛЯЕМ коллекцию, а получаем существующую или создаём новую
try:
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Коллекция '{COLLECTION_NAME}' уже существует, добавляем новые документы...")
except:
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    print(f"Коллекция '{COLLECTION_NAME}' создана...")

# Загружаем уже существующие ID документов (чтобы не дублировать)
existing_ids = set()
try:
    existing = collection.get()
    existing_ids = set(existing['ids'])
    print(f"Найдено уже загруженных документов: {len(existing_ids)}")
except:
    pass

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
    length_function=len
)

total_chunks = 0
files_processed = 0
for filename in os.listdir(XML_DIR):
    if not filename.endswith(".xml"):
        continue
    filepath = os.path.join(XML_DIR, filename)
    try:
        # Пропускаем уже загруженные файлы (по ID)
        doc_id = filename.replace(".xml", "")
        if doc_id in existing_ids:
            continue
            
        tree = ET.parse(filepath)
        root = tree.getroot()
        text_elem = root.find(".//text")
        if text_elem is None or not text_elem.text:
            continue
        text = text_elem.text.strip()
        if not text:
            continue
        id_elem = root.find(".//id")
        doc_id = id_elem.text if id_elem is not None else filename.replace(".xml", "")
        chunks = text_splitter.split_text(text)
        for chunk_idx, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{chunk_idx}"
            collection.add(
                ids=[chunk_id],
                documents=[chunk],
                metadatas=[{"source": doc_id, "filename": filename}]
            )
            total_chunks += 1
        files_processed += 1
        if files_processed % 100 == 0:
            print(f"Добавлено {files_processed} новых файлов, создано {total_chunks} чанков")
    except Exception as e:
        print(f"Ошибка в {filename}: {e}")

print(f"Готово! Добавлено {files_processed} новых файлов, всего чанков: {total_chunks}")
