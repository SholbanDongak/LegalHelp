import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    """Проверяем, что сервер отвечает на /api/health"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["service"] == "LegalHelp"
    assert response.json()["status"] == "ok"

def test_process_request_with_manual_text():
    """Проверяем обработку ручного текста"""
    response = client.post(
        "/api/process",
        data={
            "manual_text": "Требуем предоставить документы за 2023 год",
            "company_name": "ООО Тест",
            "inn": "1234567890"
        }
    )
    assert response.status_code == 200
    assert response.json()["document_type"] == "fns"
    assert response.json()["company_name"] == "ООО Тест"
    assert response.json()["status"] == "success"

def test_process_request_missing_data():
    """Проверяем, что сервер возвращает ошибку при отсутствии данных"""
    response = client.post(
        "/api/process",
        data={
            "company_name": "ООО Тест",
            "inn": "1234567890"
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()

def test_document_classification():
    """Проверяем классификатор документов"""
    from src.document_classifier import classify_document
    
    assert classify_document("Требование налоговой") == "fns"
    assert classify_document("Определение суда") == "court"
    assert classify_document("Претензия по договору") == "counterparty"
    assert classify_document("Что-то непонятное") == "other"
