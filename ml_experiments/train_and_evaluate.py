"""
Обучение и сравнение моделей для классификации релевантности чанков.
Baseline: Logistic Regression (TF-IDF).
Модели: Decision Tree, Random Forest, Gradient Boosting.
Метрики: Accuracy, Precision, Recall, F1, ROC-AUC.
Графики: ROC, confusion matrix, feature importance, сравнение моделей.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import learning_curve, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

DATASET = "ml_experiments/dataset.csv"
PLOTS_DIR = "ml_experiments/plots"
RESULTS_MD = "ml_experiments/results.md"

os.makedirs(PLOTS_DIR, exist_ok=True)

df = pd.read_csv(DATASET)
print(
    f"Загружено {len(df)} примеров. Баланс классов: {df['relevant'].value_counts().to_dict()}"
)

text_features = "chunk"
numeric_features = [
    "chunk_length",
    "query_length",
    "rank",
]

preprocessor = ColumnTransformer(
    [
        ("tfidf", TfidfVectorizer(max_features=300, ngram_range=(1, 2)), text_features),
        ("num", StandardScaler(), numeric_features),
    ]
)

X = df[[text_features] + numeric_features]
y = df["relevant"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

models = {
    "Logistic Regression (baseline)": LogisticRegression(
        max_iter=1000, random_state=42
    ),
    "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
}

results = []
roc_data = {}
conf_matrices = {}
trained_models = {}

for name, model in models.items():
    pipe = Pipeline([("prep", preprocessor), ("clf", model)])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_proba = (
        pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else None
    )

    results.append(
        {
            "Model": name,
            "Accuracy": accuracy_score(y_test, y_pred),
            "Precision": precision_score(y_test, y_pred, zero_division=0),
            "Recall": recall_score(y_test, y_pred, zero_division=0),
            "F1": f1_score(y_test, y_pred, zero_division=0),
            "ROC-AUC": roc_auc_score(y_test, y_proba) if y_proba is not None else None,
        }
    )
    if y_proba is not None:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_data[name] = (fpr, tpr)
    conf_matrices[name] = confusion_matrix(y_test, y_pred)
    trained_models[name] = pipe
    print(f"\n=== {name} ===")
    print(classification_report(y_test, y_pred, zero_division=0))

results_df = pd.DataFrame(results).sort_values("ROC-AUC", ascending=False)
print("\n=== ИТОГОВАЯ ТАБЛИЦА ===")
print(results_df.to_string(index=False))

# График: сравнение моделей
plt.figure(figsize=(12, 6))
metrics = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
x = np.arange(len(results_df))
width = 0.15
for i, m in enumerate(metrics):
    plt.bar(x + i * width, results_df[m], width, label=m)
plt.xticks(x + width * 2, results_df["Model"], rotation=15)
plt.ylabel("Значение")
plt.title("Сравнение моделей по метрикам")
plt.legend()
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/model_comparison.png", dpi=150)
plt.close()

# График: ROC-кривые
plt.figure(figsize=(8, 6))
for name, (fpr, tpr) in roc_data.items():
    auc = roc_auc_score(y_test, trained_models[name].predict_proba(X_test)[:, 1])
    plt.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
plt.plot([0, 1], [0, 1], "k--", label="Случайное угадывание")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC-кривые моделей")
plt.legend()
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/roc_curves.png", dpi=150)
plt.close()

# График: confusion matrices
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for ax, (name, cm) in zip(axes.ravel(), conf_matrices.items()):
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax, cbar=False)
    ax.set_title(name)
    ax.set_xlabel("Предсказано")
    ax.set_ylabel("Истинно")
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/confusion_matrices.png", dpi=150)
plt.close()

# График: feature importance (Random Forest)
best_rf = trained_models["Random Forest"]
prep = best_rf.named_steps["prep"]
clf = best_rf.named_steps["clf"]
tfidf_names = prep.named_transformers_["tfidf"].get_feature_names_out()
feature_names = list(tfidf_names) + numeric_features
importances = clf.feature_importances_
idx = np.argsort(importances)[-15:]
plt.figure(figsize=(10, 6))
plt.barh(np.array(feature_names)[idx], importances[idx])
plt.xlabel("Важность")
plt.title("Топ-15 признаков (Random Forest)")
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/feature_importance.png", dpi=150)
plt.close()

# График: learning curve
train_sizes, train_scores, val_scores = learning_curve(
    trained_models["Random Forest"],
    X,
    y,
    cv=3,
    n_jobs=-1,
    train_sizes=np.linspace(0.1, 1.0, 8),
)
plt.figure(figsize=(8, 6))
plt.plot(train_sizes, train_scores.mean(axis=1), "o-", label="Train")
plt.plot(train_sizes, val_scores.mean(axis=1), "o-", label="Validation")
plt.xlabel("Размер обучающей выборки")
plt.ylabel("Accuracy")
plt.title("Learning curve (Random Forest)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/learning_curve.png", dpi=150)
plt.close()

# Сохранение результатов
with open(RESULTS_MD, "w", encoding="utf-8") as f:
    f.write("# Результаты ML-экспериментов\n\n")
    f.write("## Сравнение моделей\n\n")
    f.write(results_df.to_markdown(index=False))
    f.write("\n\n## Графики\n\n")
    f.write("![Сравнение моделей](plots/model_comparison.png)\n\n")
    f.write("![ROC-кривые](plots/roc_curves.png)\n\n")
    f.write("![Confusion matrices](plots/confusion_matrices.png)\n\n")
    f.write("![Feature importance](plots/feature_importance.png)\n\n")
    f.write("![Learning curve](plots/learning_curve.png)\n")

print(f"\n✅ Готово. Графики: {PLOTS_DIR}/, результаты: {RESULTS_MD}")
