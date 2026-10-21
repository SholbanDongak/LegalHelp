import uuid
from datetime import datetime

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.ai_generator import generate_answer
from src.document_generator import generate_document, list_available_templates
from src.utils.ai_agent import analyze_request

app = FastAPI(title="LegalHelp API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "LegalHelp"}


# Монтируем папку output для скачивания документов
app.mount("/output", StaticFiles(directory="output"), name="output")


@app.post("/api/process")
async def process_request(
    file: UploadFile = File(None),
    manual_text: str = Form(None),
    company_name: str = Form(...),
    inn: str = Form(...),
    document_type: str = Form("other"),
):
    try:
        if file:
            content = await file.read()
            request_text = content.decode("utf-8", errors="ignore")[:2000]
        else:
            request_text = manual_text or ""
        answer = generate_answer(request_text, company_name, inn, document_type)
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "document_type": document_type,
            "company_name": company_name,
            "inn": inn,
            "request_text": request_text[:500],
            "draft_answer": answer,
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Монтируем папку output для скачивания документов
app.mount("/output", StaticFiles(directory="output"), name="output")


@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """
    Чат с AI-агентом.

    Request body:
    {
        "message": "текст сообщения пользователя",
        "history": [{"role": "user", "content": "..."}, ...] (опционально)
    }

    Returns:
    {
        "response": "текст ответа AI",
        "agent_metadata": {
            "doc_type": "тип документа",
            "doc_label": "название типа",
            "confidence": 0.0-1.0,
            "entities": {...},
            "duty": {...},
            "questions": [...]
        }
    }
    """
    try:
        message = request.get("message", "")
        history = request.get("history", [])

        if not message:
            return {"response": "Пожалуйста, задайте вопрос.", "agent_metadata": None}

        # 1. Анализируем запрос через AI-агент
        print(f"\n🤖 AI-агент анализирует: '{message[:100]}...'")
        agent_analysis = analyze_request(message)

        # 2. Генерируем ответ через RAG
        print(f"🔍 Генерируем ответ через RAG...")
        answer = generate_answer(message, "", "", "other")

        # 3. Формируем метаданные
        metadata = {
            "doc_type": agent_analysis["classification"]["doc_type"],
            "doc_label": agent_analysis["classification"]["label"],
            "confidence": agent_analysis["classification"]["confidence"],
            "entities": agent_analysis["entities"],
            "duty": agent_analysis["duty"],
            "questions": agent_analysis["questions"],
        }

        print(
            f"✅ AI-агент определил: {metadata['doc_label']} ({metadata['confidence']:.0%})"
        )

        return {"response": answer, "agent_metadata": metadata}

    except Exception as e:
        print(f"❌ Ошибка в /api/chat: {e}")
        import traceback

        traceback.print_exc()
        return {
            "response": f"Извините, произошла ошибка: {str(e)}",
            "agent_metadata": None,
        }


@app.post("/api/generate-document")
async def api_generate_document(request: dict):
    """
    Генерация юридического документа.

    Request body:
    {
        "query": "текст запроса пользователя",
        "output_format": "docx|pdf|both" (по умолчанию "both"),
        "force_doc_type": "тип документа" (опционально),
        "user_fields": {"court_name": "...", "plaintiff_name": "..."} (опционально)
    }

    Returns:
    {
        "success": true/false,
        "doc_type": "тип документа",
        "confidence": 0.0-1.0,
        "fields": {...},
        "filled_text": "...",
        "docx_url": "/output/documents/...",
        "pdf_url": "/output/documents/...",
        "error": "описание ошибки"
    }
    """
    try:
        query = request.get("query", "")
        output_format = request.get("output_format", "both")
        force_doc_type = request.get("force_doc_type")
        user_fields = request.get("user_fields")

        if not query:
            return {"success": False, "error": "Поле 'query' обязательно"}

        # Генерируем документ
        result = await generate_document(
            user_query=query,
            output_format=output_format,
            force_doc_type=force_doc_type,
            user_fields=user_fields,
        )

        # Формируем URL-ы для скачивания
        if result.get("docx_path"):
            result["docx_url"] = result["docx_path"].replace("./", "/")
        if result.get("pdf_path"):
            result["pdf_url"] = result["pdf_path"].replace("./", "/")

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/templates")
async def api_list_templates():
    """
    Возвращает список доступных шаблонов документов.
    """
    templates = list_available_templates()
    return {"templates": templates}
