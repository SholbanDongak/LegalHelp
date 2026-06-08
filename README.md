# LegalHelp — AI-ассистент для ответов на входящие документы

**Автор:** Шолбан Донгак  
**Репозиторий:** [GitHub](https://github.com/SholbanDongak/LegalHelp)

## О проекте

LegalHelp генерирует юридически корректные черновики ответов на запросы госорганов, судебные акты, письма контрагентов.

Проект полностью локальный: React + FastAPI + Ollama + Qwen2.5 + ChromaDB.

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| Бэкенд | Python 3.11 + FastAPI |
| База знаний (векторная) | ChromaDB |
| OCR | EasyOCR + Tesseract |
| Локальная LLM | Ollama + Qwen2.5:7b-instruct |
| Фронтенд | React + Vite |

## Установка и запуск

1. Установите Ollama, скачайте модель: `ollama pull qwen2.5:7b-instruct`
2. Запустите сервер Ollama: `ollama serve`
3. В другом терминале: `cd ~/LegalHelp`, `source legal_env/bin/activate`, `pip install -r requirements.txt`, `uvicorn src.main:app --reload --port 8000`
4. В третьем терминале: `cd ~/legal-frontend`, `npm install`, `npm run dev`
5. Откройте `http://localhost:5173`

## API

- `POST /api/process` – параметры `company_name`, `inn`, `document_type`, `manual_text`
- `GET /api/health`

## Лицензия

MIT

## Автор

Шолбан Донгак – проектный практикум.
