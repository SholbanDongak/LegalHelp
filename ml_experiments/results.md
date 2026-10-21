Результаты ML-экспериментов

Сравнение моделей

| Model                          |   Accuracy |   Precision |   Recall |       F1 |   ROC-AUC |
|:-------------------------------|-----------:|------------:|---------:|---------:|----------:|
| Logistic Regression (baseline) |        0.8 |    0.714286 |      1   | 0.833333 |       1   |
| Random Forest                  |        1   |    1        |      1   | 1        |       1   |
| Gradient Boosting              |        1   |    1        |      1   | 1        |       1   |
| Decision Tree                  |        0.8 |    0.8      |      0.8 | 0.8      |       0.8 |

Графики

![Сравнение моделей](plots/model_comparison.png)

![ROC-кривые](plots/roc_curves.png)

![Confusion matrices](plots/confusion_matrices.png)

![Feature importance](plots/feature_importance.png)

![Learning curve](plots/learning_curve.png)

Ограничения эксперимента

- Датасет курированный вручную: 31 пример (15 positive — реальные статьи ГК, ТК, ГПК, АПК, СК, ФЗ; 16 negative — нерелевантные чанки, включая 6 «сложных» со «Статья N»).
- Признаки без утечек: TF-IDF по тексту + `chunk_length` + `query_length` + `rank`. Убраны `bm25_hint`, `num_legal_terms`, `has_article_number` — они дублировали метку.
- Малая тестовая выборка: 10 примеров (сплит 70/30). Random Forest и Gradient Boosting дали 1.0 — это следствие малого теста, а не идеальной модели. На 500+ примерах ожидаются 0.85–0.92.
- Для production: 500+ примеров, ручная разметка юристом, кросс-валидация (k-fold).
- База ChromaDB содержит не только кодексы, но и подзаконные акты — для production нужна фильтрация по типу документа.
