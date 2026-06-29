"""
Главный модуль генерации юридических документов.
Объединяет все компоненты: маппинг → извлечение полей → экспорт.
"""
import asyncio
import os
from datetime import datetime
from typing import Dict, Optional, Tuple

from src.document_generator.template_mapper import map_query_to_template
from src.document_generator.field_extractor import extract_fields
from src.document_generator.docx_exporter import (
    load_template_text, fill_template, create_docx, ensure_output_dir
)
from src.document_generator.pdf_exporter import create_pdf


async def generate_document(
    user_query: str,
    output_format: str = "both",
    force_doc_type: Optional[str] = None
) -> Dict:
    """
    Главный пайплайн генерации документа.
    
    Args:
        user_query: Текст запроса пользователя
        output_format: Формат вывода ("docx", "pdf" или "both")
        force_doc_type: Принудительный тип документа (если None — определяется автоматически)
    
    Returns:
        Словарь с результатами:
        {
            "success": True/False,
            "doc_type": тип документа,
            "confidence": уверенность классификации,
            "fields": извлечённые поля,
            "filled_text": заполненный текст,
            "docx_path": путь к DOCX (если создан),
            "pdf_path": путь к PDF (если создан),
            "error": описание ошибки (если есть)
        }
    """
    result = {
        "success": False,
        "doc_type": None,
        "confidence": 0.0,
        "fields": {},
        "filled_text": "",
        "docx_path": None,
        "pdf_path": None,
        "error": None
    }
    
    try:
        # Шаг 1: Определяем тип документа
        if force_doc_type:
            doc_type = force_doc_type
            confidence = 1.0
        else:
            doc_type, confidence = map_query_to_template(user_query)
        
        if not doc_type:
            result["error"] = "Не удалось определить тип документа. Попробуйте сформулировать запрос более конкретно."
            return result
        
        result["doc_type"] = doc_type
        result["confidence"] = confidence
        print(f"📋 Тип документа: {doc_type} (уверенность: {confidence:.2f})")
        
        # Шаг 2: Загружаем шаблон
        template = load_template_text(doc_type)
        if not template:
            result["error"] = f"Шаблон для типа '{doc_type}' не найден"
            return result
        
        # Шаг 3: Извлекаем поля из запроса
        fields = await extract_fields(user_query, doc_type)
        result["fields"] = fields
        print(f"📝 Извлечено полей: {len([v for v in fields.values() if v])}")
        
        # Шаг 4: Заполняем шаблон
        filled_text = fill_template(template, fields)
        result["filled_text"] = filled_text
        
        # Шаг 5: Создаём файлы
        ensure_output_dir()
        
        if output_format in ("docx", "both"):
            docx_path = create_docx(filled_text, doc_type, fields)
            result["docx_path"] = docx_path
        
        if output_format in ("pdf", "both"):
            pdf_path = create_pdf(filled_text, doc_type, fields)
            result["pdf_path"] = pdf_path
        
        result["success"] = True
        print(f"✅ Документ успешно сгенерирован!")
        
    except Exception as e:
        result["error"] = f"Ошибка при генерации документа: {str(e)}"
        print(f"❌ {result['error']}")
    
    return result


def list_available_templates() -> Dict[str, str]:
    """
    Возвращает список доступных шаблонов документов.
    
    Returns:
        Словарь {doc_type: описание}
    """
    templates_dir = "./templates"
    templates = {}
    
    descriptions = {
        "claim_consumer": "Иск о защите прав потребителей",
        "claim_labor_wage": "Иск о взыскании заработной платы",
        "claim_labor_reinstatement": "Иск о восстановлении на работе",
        "claim_divorce": "Исковое заявление о разводе",
        "claim_alimony": "Исковое заявление о взыскании алиментов",
        "claim_parental_rights": "Иск о лишении/ограничении родительских прав",
        "claim_housing": "Исковое заявление по жилищным вопросам",
        "claim_land": "Иск по земельным спорам",
        "claim_arbitration": "Исковое заявление в арбитражный суд",
        "claim_civil_general": "Общее исковое заявление в суд",
        "claim_tax": "Иск по налоговым спорам",
        "appeal_civil": "Апелляционная жалоба (гражданское дело)",
        "appeal_arbitration": "Апелляционная жалоба (арбитраж)",
        "appeal_admin_procedure": "Жалоба в административном порядке",
        "cassation_civil": "Кассационная жалоба (гражданское дело)",
        "cassation_arbitration": "Кассационная жалоба (арбитраж)",
        "cassation_kas": "Кассационная жалоба (КАС РФ)",
        "complaint_koap": "Жалоба на постановление по КоАП",
        "objection_to_court_order": "Возражение на судебный приказ",
        "application_for_court_order": "Заявление на выдачу судебного приказа",
        "application_to_cancel_default_judgment": "Заявление об отмене заочного решения",
        "private_complaint": "Частная жалоба",
        "supervisory_complaint": "Надзорная жалоба",
        "admin_claim_kas": "Административное исковое заявление (КАС РФ)"
    }
    
    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith(".txt"):
                doc_type = filename[:-4]
                templates[doc_type] = descriptions.get(doc_type, doc_type)
    
    return templates


async def test_full_pipeline():
    """Тест полного пайплайна."""
    print("🧪 ТЕСТ ПОЛНОГО ПАЙПЛАЙНА")
    print("="*60)
    
    # Тестовый запрос
    test_query = """
    Я купил телефон Samsung Galaxy S23 в магазине Технопарк 15 января 2026 года за 80000 рублей.
    Через неделю экран начал мерцать. Хочу вернуть деньги и компенсацию морального вреда 10000 рублей.
    Магазин находится по адресу г. Кызыл, ул. Ленина, д. 10.
    """
    
    print(f"\n📝 Запрос пользователя:\n{test_query}")
    print()
    
    # Запускаем пайплайн
    result = await generate_document(test_query, output_format="both")
    
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТ:")
    print(f"   ✅ Успех: {result['success']}")
    print(f"   📋 Тип документа: {result['doc_type']}")
    print(f"   🎯 Уверенность: {result['confidence']:.2f}")
    print(f"   📝 Заполнено полей: {len([v for v in result['fields'].values() if v])}")
    
    if result['docx_path']:
        print(f"   📄 DOCX: {result['docx_path']}")
    if result['pdf_path']:
        print(f"   📄 PDF: {result['pdf_path']}")
    if result['error']:
        print(f"   ❌ Ошибка: {result['error']}")
    
    print("\n" + "="*60)
    print("📚 ДОСТУПНЫЕ ШАБЛОНЫ:")
    templates = list_available_templates()
    for doc_type, description in sorted(templates.items()):
        print(f"   - {doc_type}: {description}")


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
