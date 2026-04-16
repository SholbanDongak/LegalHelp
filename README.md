**Репозиторий:** [GitHub](https://github.com/SholbanDongak/LegalHelp) — AI-ассистент для ответов на входящие документы

**Автор:** Шолбан Донгак  
**Репозиторий:** [GitHub](https://github.com/SholbanDongak/LegalHelp)

## О проекте
LegalHelp генерирует юридически корректные черновики ответов на:
- Запросы контролирующих органов (ФНС, прокуратура, трудовая инспекция, Роскомнадзор, ФАС)
- Судебные акты (определения, иски, запросы)
- Письма контрагентов (претензии, оферты, рекламации)
- Обращения граждан и жалобы

## Целевая аудитория
| Сегмент | Сценарий использования |
|---------|------------------------|
| Малый бизнес | Ответы на запросы госорганов |
| Юридические фирмы | Черновики процессуальных документов |
| Отдел закупок | Ответы на жалобы и запросы ФАС |
| Руководители | Переписка с контрагентами |

## Технологический стек (РФ-совместимый)
| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.11 + FastAPI |
| База данных | PostgreSQL |
| OCR | EasyOCR + Tesseract |
| LLM | YandexGPT |
| Контейнеризация | Docker |
| CI/CD | GitHub Actions |

## API Эндпоинты
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/process` | Анализ документа → генерация ответа |
| GET | `/api/health` | Проверка работоспособности |

## Запуск
```bash
# 1. Клонировать
git clone https://github.com/SholbanDongak/practice_2_team_11.git
cd practice_2_team_11

# 2. Виртуальное окружение
python -m venv venv
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить PostgreSQL через Docker
docker-compose up -d

# 5. Запустить приложение
uvicorn src.main:app --reload --port 8000
curl -X POST http://localhost:8000/api/process \
  -F "file=@request.pdf" \
  -F "company_name=ООО Ромашка" \
  -F "inn=1234567890" \
  -F "document_type=request_fns"

---

## ✅ ВТОРОЙ ШАГ — ДОБАВЛЯЕМ КЛАССИФИКАТОР ТИПОВ ДОКУМЕНТОВ

```bash
cat > src/document_classifier.py << 'EOF'
"""Классификация типа входящего документа"""

def classify_document(text: str) -> str:
    """
    Определяет тип документа по тексту.
    Возвращает: fns, court, counterparty, roskomnadzor, fas, labor_inspection, prosecutor, other
    """
    text_lower = text.lower()
    
    # ФНС
    if any(word in text_lower for word in ['налоговая', 'фнс', 'предоставить документы', 'требование о представлении']):
        return "fns"
    
    # Прокуратура
    if any(word in text_lower for word in ['прокуратура', 'прокурор', 'представление прокурора']):
        return "prosecutor"
    
    # Суд
    if any(word in text_lower for word in ['суд', 'определение', 'исковое заявление', 'судебное заседание']):
        return "court"
    
    # Контрагент
    if any(word in text_lower for word in ['претензия', 'оферта', 'договор', 'рекламация', 'требование оплаты']):
        return "counterparty"
    
    # Роскомнадзор
    if any(word in text_lower for word in ['роскомнадзор', 'персональные данные', '152-фз']):
        return "roskomnadzor"
    
    # ФАС
    if any(word in text_lower for word in ['фас', 'антимонопольная', 'жалоба', 'нарушение антимонопольного']):
        return "fas"
    
    # Трудовая инспекция
    if any(word in text_lower for word in ['трудовая инспекция', 'гит', 'охрана труда', 'трудовой кодекс']):
        return "labor_inspection"
    
    return "other"
 
