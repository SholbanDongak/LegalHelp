import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

models = {
    "all-MiniLM-L6-v2": SentenceTransformer("all-MiniLM-L6-v2"),
    "intfloat/multilingual-e5-large": SentenceTransformer("intfloat/multilingual-e5-large"),
    "cointegrated/rubert-tiny2": SentenceTransformer("cointegrated/rubert-tiny2")
}

test_pairs = [
    ("неустойка по ГК РФ", "Неустойка – денежная сумма, которую должник обязан уплатить кредитору при просрочке"),
    ("апелляционная жалоба", "Статья 320 ГПК РФ: право апелляционного обжалования решений суда"),
    ("возражение на судебный приказ", "Должник вправе подать возражение в течение 10 дней со дня получения приказа")
]

results = {}
for name, model in models.items():
    scores = []
    for question, answer in test_pairs:
        emb_q = model.encode(question)
        emb_a = model.encode(answer)
        sim = cosine_similarity([emb_q], [emb_a])[0][0]
        scores.append(sim)
    results[name] = np.mean(scores)
    print(f"{name}: средняя косинусная близость = {np.mean(scores):.4f}")

plt.figure(figsize=(8, 5))
plt.bar(results.keys(), results.values(), color=['skyblue', 'orange', 'lightgreen'])
plt.xlabel("Модель эмбеддингов")
plt.ylabel("Средняя косинусная близость")
plt.title("Сравнение моделей эмбеддингов для юридических текстов")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("ml_experiments/results/embedding_comparison.png", dpi=150)
plt.show()

best_model = max(results, key=results.get)
print(f"\n✅ Лучшая модель: {best_model}")
