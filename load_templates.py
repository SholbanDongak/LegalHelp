import os
import chromadb
from chromadb.utils import embedding_functions

TEMPLATES_DIR = "./templates"
CHROMA_PATH = "./legal_chromadb"
COLLECTION_NAME = "templates"
MODEL_NAME = "all-MiniLM-L6-v2"

print("Подключение к ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)

# Удаляем старую коллекцию, чтобы пересоздать с новыми метаданными
try:
    client.delete_collection(COLLECTION_NAME)
    print("Старая коллекция удалена")
except:
    pass

collection = client.create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)

docs_count = 0
for root, dirs, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if file.endswith(".txt"):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            rel_path = os.path.relpath(filepath, TEMPLATES_DIR)
            category = rel_path.split(os.sep)[0] if os.sep in rel_path else "other"
            template_type = file.replace(".txt", "")   # имя файла без расширения
            doc_id = f"{category}_{template_type}"
            collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[{
                    "source": "template",
                    "category": category,
                    "full_path": rel_path,
                    "filename": file,
                    "template_type": template_type
                }]
            )
            docs_count += 1
            print(f"Добавлен: {doc_id} (тип: {template_type})")

print(f"Загружено шаблонов: {docs_count}")
