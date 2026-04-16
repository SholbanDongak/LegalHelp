import os
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Импортируем наши модули
from src.document_classifier import classify_document
from src.ai_generator import generate_answer
from src.ocr.extractor import extract_text_from_file

load_dotenv()

app = FastAPI(
    title="LegalHelp API",
    description="AI-ассистент для ответов на входящие документы",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "LegalHelp", "version": "0.3.0"}

@app.post("/api/process")
async def process_request(
    file: UploadFile = File(None),
    manual_text: str = Form(None),
    company_name: str = Form(...),
    inn: str = Form(...),
    document_type: str = Form("auto")
):
    """
    Генерация ответа на входящий документ.
    
    Параметры:
    - file: PDF, JPEG, PNG файл с запросом
    - manual_text: текст запроса (если нет файла)
    - company_name: название компании
    - inn: ИНН компании
    - document_type: тип документа (auto/fns/prosecutor/court/counterparty/etc)
    """
    
    # 1. Получаем текст запроса
    request_text = None
    
    if file and file.filename:
        # Сохраняем файл временно
        temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        
        try:
            # Распознаём текст через OCR
            request_text = extract_text_from_file(temp_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка OCR: {str(e)}")
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    elif manual_text:
        request_text = manual_text
    
    else:
        raise HTTPException(
            status_code=400, 
            detail="Необходимо загрузить файл или ввести текст запроса"
        )
    
    if not request_text or len(request_text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Не удалось распознать текст. Попробуйте загрузить более качественный файл или введите текст вручную."
        )
    
    # 2. Определяем тип документа (если не указан явно)
    if document_type == "auto":
        doc_type = classify_document(request_text)
    else:
        doc_type = document_type
    
    # 3. Генерируем ответ через YandexGPT
    answer = generate_answer(request_text, company_name, inn, doc_type)
    
    # 4. Возвращаем результат
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
