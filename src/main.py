import os
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.classifiers.rule_based import RuleBasedClassifier
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

classifier = RuleBasedClassifier()


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
    request_text = None

    if file and file.filename:
        temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        try:
            request_text = extract_text_from_file(temp_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка OCR: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    elif manual_text:
        request_text = manual_text

    else:
        raise HTTPException(status_code=400, detail="Необходимо загрузить файл или ввести текст")

    if not request_text or len(request_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Не удалось распознать текст")

    if document_type == "auto":
        doc_type = classifier.predict(request_text)
        confidence = classifier.predict_with_confidence(request_text)[1]
    else:
        doc_type = document_type
        confidence = 1.0

    answer = generate_answer(request_text, company_name, inn, doc_type)

    return {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "document_type": doc_type,
        "confidence": confidence,
        "company_name": company_name,
        "inn": inn,
        "request_text": request_text[:500] + "..." if len(request_text) > 500 else request_text,
        "draft_answer": answer,
        "status": "success"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
