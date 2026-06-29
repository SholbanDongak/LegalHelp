"""
Извлечение полей из запроса пользователя с помощью LLM.
"""
import asyncio
import json
import re
from typing import Dict, Any, Optional
from ollama import AsyncClient

MODEL_NAME = "llama3.1:8b"

# Схема полей для разных типов документов
FIELD_SCHEMAS = {
    "claim_consumer": {
        "court_name": "Наименование суда",
        "plaintiff_name": "ФИО истца",
        "plaintiff_address": "Адрес истца",
        "defendant_name": "Наименование ответчика (продавец/исполнитель)",
        "defendant_address": "Адрес ответчика",
        "product_name": "Наименование товара/услуги",
        "amount": "Сумма (число)",
        "defect_description": "Описание недостатка",
        "moral_damage": "Сумма морального вреда (число)",
        "date": "Дата покупки (ДД.ММ.ГГГГ)"
    },
    "claim_labor_wage": {
        "court_name": "Наименование суда",
        "plaintiff_name": "ФИО истца (работник)",
        "plaintiff_address": "Адрес истца",
        "defendant_name": "Наименование работодателя",
        "defendant_address": "Адрес работодателя",
        "employment_date": "Дата начала работы (ДД.ММ.ГГГГ)",
        "wage_period": "Период задолженности",
        "wage_amount": "Сумма задолженности (число)",
        "date": "Дата (ДД.ММ.ГГГГ)"
    },
    "claim_civil_general": {
        "court_name": "Наименование суда",
        "plaintiff_name": "ФИО истца",
        "plaintiff_address": "Адрес истца",
        "defendant_name": "ФИО/наименование ответчика",
        "defendant_address": "Адрес ответчика",
        "claim_description": "Описание требований",
        "amount": "Сумма иска (число)",
        "grounds": "Основания иска",
        "date": "Дата (ДД.ММ.ГГГГ)"
    },
    "appeal_civil": {
        "appeal_court_name": "Наименование апелляционного суда",
        "applicant_name": "ФИО заявителя",
        "applicant_address": "Адрес заявителя",
        "case_number": "Номер дела",
        "judge_name": "ФИО судьи",
        "court_name": "Наименование суда первой инстанции",
        "decision_date": "Дата решения (ДД.ММ.ГГГГ)",
        "grounds": "Основания для отмены решения",
        "date": "Дата (ДД.ММ.ГГГГ)"
    }
}

async def extract_fields(user_query: str, doc_type: str) -> Dict[str, Any]:
    """
    Извлекает поля из запроса пользователя с помощью LLM.
    
    Args:
        user_query: Текст запроса пользователя
        doc_type: Тип документа (например, "claim_consumer")
    
    Returns:
        Словарь с извлечёнными полями
    """
    schema = FIELD_SCHEMAS.get(doc_type, {})
    
    if not schema:
        print(f"⚠️  Схема для типа {doc_type} не найдена")
        return {}
    
    # Формируем промпт для LLM
    schema_text = "\n".join([f"- {key}: {desc}" for key, desc in schema.items()])
    
    system_prompt = f"""Ты — помощник для заполнения юридических документов.
Извлеки из текста пользователя следующие поля и верни их в формате JSON.

ПОЛЯ ДЛЯ ИЗВЛЕЧЕНИЯ:
{schema_text}

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:
1. Извлекай ТОЛЬКО информацию, которая ЕСТЬ в тексте пользователя.
2. Если поле НЕ УКАЗАНО в тексте, верни для него null.
3. НИКОГДА не придумывай данные, которых нет в тексте.
4. Для числовых полей (amount, wage_amount, moral_damage) извлеки только число.
5. Для дат используй формат ДД.ММ.ГГГГ.
6. Верни ТОЛЬКО JSON, без дополнительного текста.

ПРИМЕР ПРАВИЛЬНОГО ОТВЕТА (если ФИО не указано):
{{"court_name": null, "plaintiff_name": null, "amount": "50000"}}"""
    
    user_prompt = f"Текст пользователя:\n{user_query}"
    
    try:
        client = AsyncClient(host='http://127.0.0.1:11434')
        response = await client.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 512
            }
        )
        
        answer = response['message']['content']
        
        # Извлекаем JSON из ответа
        json_match = re.search(r'\{[^}]+\}', answer, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            fields = json.loads(json_str)
            
            # Заменяем пустые строки на null
            for key in fields:
                if fields[key] == "":
                    fields[key] = None
            
            print(f"✅ Извлечено полей: {len(fields)}")
            return fields
        else:
            print(f"⚠️  JSON не найден в ответе LLM")
            return {}
            
    except Exception as e:
        print(f"❌ Ошибка извлечения полей: {e}")
        return {}


def test_extraction():
    """Тест извлечения полей."""
    test_query = """
    Я купил телефон Samsung Galaxy S23 в магазине Технопарк 15 января 2026 года за 80000 рублей.
    Через неделю экран начал мерцать. Хочу вернуть деньги и компенсацию морального вреда 10000 рублей.
    Магазин находится по адресу г. Кызыл, ул. Ленина, д. 10.
    Мой адрес: г. Кызыл, ул. Пушкина, д. 5, кв. 15.
    """
    
    print("🧪 ТЕСТ ИЗВЛЕЧЕНИЯ ПОЛЕЙ (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("="*60)
    print(f"Запрос: {test_query}")
    print()
    
    fields = asyncio.run(extract_fields(test_query, "claim_consumer"))
    
    print("\n✅ Извлечённые поля:")
    for key, value in fields.items():
        if value is None:
            print(f"  {key}: null (не указано)")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    test_extraction()
