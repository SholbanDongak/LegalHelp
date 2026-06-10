import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.ai_generator import generate_answer

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

@app.post("/api/process")
async def process_request(
    file: UploadFile = File(None),
    manual_text: str = Form(None),
    company_name: str = Form(...),
    inn: str = Form(...),
    document_type: str = Form("other")
):
    try:
        if file:
            content = await file.read()
            request_text = content.decode('utf-8', errors='ignore')[:2000]
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
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))