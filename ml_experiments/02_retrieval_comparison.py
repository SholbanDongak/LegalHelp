import matplotlib.pyplot as plt
import numpy as np

# Данные из вашего README (результаты экспериментов)
strategies = ['Векторный поиск', 'Гибридный поиск']
precision = [0.62, 0.87]
recall = [0.58, 0.84]
mrr = [0.58, 0.84]

x = np.arange(len(strategies))
width = 0.25

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width, precision, width, label='Precision@5', color='skyblue')
ax.bar(x, recall, width, label='Recall@5', color='lightgreen')
ax.bar(x + width, mrr, width, label='MRR', color='orange')

ax.set_xlabel('Стратегия поиска')
ax.set_ylabel('Значение метрики')
ax.set_title('Сравнение стратегий поиска: Vector vs Hybrid')
ax.set_xticks(x)
ax.set_xticklabels(strategies)
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.savefig('ml_experiments/results/retrieval_comparison.png', dpi=150)
plt.show()

print("\n✅ График создан на основе результатов экспериментов")
print("📊 Результаты:")
print(f"   Precision@5: векторный={precision[0]}, гибридный={precision[1]} (прирост {((precision[1]-precision[0])/precision[0])*100:.1f}%)")
print(f"   Recall@5:    векторный={recall[0]}, гибридный={recall[1]} (прирост {((recall[1]-recall[0])/recall[0])*100:.1f}%)")
print(f"   MRR:         векторный={mrr[0]}, гибридный={mrr[1]} (прирост {((mrr[1]-mrr[0])/mrr[0])*100:.1f}%)")
print("\n✅ Вывод: гибридный поиск (BM25 + эмбеддинги) превосходит векторный на 25-40%")
