import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()

app = FastAPI(title="LegalHelp", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "LegalHelp", "version": "0.2.0"}

@app.post("/api/process")
async def process_request(
    file: UploadFile = File(None),
    manual_text: str = Form(None),
    company_name: str = Form(...),
    inn: str = Form(...),
    document_type: str = Form("auto")
):
    """
    Генерация ответа на входящий документ
    """
    from src.document_classifier import classify_document
    from src.ai_generator import generate_answer
    
    # 1. Получаем текст запроса
    if file:
        # Пока заглушка для OCR
        request_text = f"[Текст будет распознан из файла: {file.filename}]"
    elif manual_text:
        request_text = manual_text
    else:
        raise HTTPException(status_code=400, detail="Загрузите файл или введите текст")
    
    # 2. Определяем тип документа
    if document_type == "auto":
        doc_type = classify_document(request_text)
    else:
        doc_type = document_type
    
    # 3. Генерируем ответ через YandexGPT
    answer = generate_answer(request_text, company_name, inn, doc_type)
    
    return {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "document_type": doc_type,
        "company_name": company_name,
        "inn": inn,
        "request_text": request_text[:500] + "..." if len(request_text) > 500 else request_text,
        "draft_answer": answer,
        "status": "success"
    }
