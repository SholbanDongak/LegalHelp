import os
import xml.etree.ElementTree as ET
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# Путь к папке с XML-файлами законов (уже есть после распаковки RusLawOD)
XML_DIR = "./RusLawOD_XML"
CHUNK_SIZE = 1000          # размер фрагмента текста для эмбеддинга
CHUNK_OVERLAP = 200        # перекрытие между фрагментами
MODEL_NAME = "all-MiniLM-L6-v2"   # модель для эмбеддингов

print("Загрузка модели эмбеддингов...")
embedder = SentenceTransformer(MODEL_NAME)

print("Подключение к ChromaDB...")
client = chromadb.PersistentClient(path="./legal_chromadb")
collection_name = "ruslawod"
try:
    client.delete_collection(collection_name)   # удаляем старую, если есть
except:
    pass
collection = client.create_collection(
    name=collection_name,
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
    length_function=len
)

total_chunks = 0
files_processed = 0

# Перебираем все XML-файлы в папке
for filename in os.listdir(XML_DIR):
    if not filename.endswith(".xml"):
        continue
    filepath = os.path.join(XML_DIR, filename)
    try:
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

        # Для быстрой проверки на защите обработаем только первые 200 файлов
        # (можно убрать или увеличить число, когда будет время на полную базу)
##        if files_processed >= 200:
##            break

        if files_processed % 100 == 0:
            print(f"Обработано {files_processed} файлов, создано {total_chunks} чанков")
    except Exception as e:
        print(f"Ошибка в {filename}: {e}")

print(f"Готово! Файлов: {files_processed}, чанков: {total_chunks}")