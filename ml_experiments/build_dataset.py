"""
Собирает датасет для классификации релевантности чанков.
Берёт запросы и находит для них топ-5 чанков через гибридный поиск.
Метка: 1, если чанк содержит ключевые слова из запроса, иначе 0.
"""

import csv
import re

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "./legal_chromadb"
COLLECTION_NAME = "ruslawod"
MODEL_NAME = "all-MiniLM-L6-v2"
OUTPUT_CSV = "ml_experiments/dataset.csv"

QUERIES = [
    "Каков срок исковой давности по договору займа?",
    "Как расторгнуть трудовой договор по инициативе работника?",
    "Какие основания для признания сделки недействительной?",
    "Каков размер госпошлины при подаче иска?",
    "Как оспорить решение суда первой инстанции?",
    "Что такое обеспечительный платёж по договору аренды?",
    "Какие права у потребителя при возврате товара?",
    "Как оформляется доверенность на представление интересов?",
    "Каков порядок наследования по закону?",
    "Какая ответственность за нарушение сроков поставки?",
]


def main():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    model = SentenceTransformer(MODEL_NAME)

    rows = []
    for query in QUERIES:
        emb = model.encode([query]).tolist()
        results = collection.query(query_embeddings=emb, n_results=5)
        chunks = results["documents"][0]
        for rank, chunk in enumerate(chunks):
            keywords = [w.lower() for w in re.findall(r"\w{5,}", query)]
            is_relevant = int(any(k in chunk.lower() for k in keywords))
            rows.append(
                {
                    "query": query,
                    "chunk": chunk,
                    "rank": rank,
                    "chunk_length": len(chunk),
                    "query_length": len(query),
                    "num_legal_terms": sum(
                        chunk.lower().count(t)
                        for t in ["статья", "пункт", "кодекс", "закон"]
                    ),
                    "has_article_number": int(
                        bool(re.search(r"статья\s+\d+", chunk.lower()))
                    ),
                    "bm25_hint": int(any(k in chunk.lower() for k in keywords)),
                    "relevant": is_relevant,
                }
            )

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Сохранено {len(rows)} строк в {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
