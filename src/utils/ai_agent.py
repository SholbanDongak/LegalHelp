"""
AI-Агент — умный помощник для граждан.
Анализирует запрос, классифицирует ситуацию, извлекает сущности,
рассчитывает госпошлину и предлагает составить документ.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import re

from src.utils.duty_calculator import ClaimType, PartyType, calculate_duty
from src.utils.llm_classifier import classify_with_llm
from src.utils.situation_classifier import classify_situation


def extract_entities(query: str) -> dict:
    """Извлекает сущности из запроса пользователя."""
    entities = {
        "sums": [],
        "dates": [],
        "names": [],
        "organizations": [],
        "addresses": [],
    }

    # ===== СУММЫ =====
    # Паттерн: 100 000, 100000, 50 тыс, 1 млн
    sum_patterns = [
        r"(\d{1,3}(?:\s\d{3})+)\s*(?:руб|₽|рублей|тысяч)",  # 100 000 руб
        r"(\d+)\s*(?:тыс|млн|тысяч)",  # 100 тыс
        r"(\d+(?:\.\d+)?)\s*(?:руб|₽)",  # 100 руб
        r"(\d{1,3}(?:\s\d{3})+)",  # просто число с пробелами > 999
        r"(\d{4,})",  # просто число > 999 без пробелов
    ]

    for pattern in sum_patterns:
        matches = re.findall(pattern, query)
        for match in matches:
            clean = match.replace(" ", "").replace(",", ".")
            if clean.replace(".", "").isdigit():
                num = float(clean)
                # Проверяем контекст для "тыс" и "млн"
                match_pos = query.find(match)
                context = query[match_pos : match_pos + 20].lower()
                if "тыс" in context:
                    num *= 1000
                elif "млн" in context:
                    num *= 1_000_000
                if num >= 100 and num not in entities["sums"]:
                    entities["sums"].append(num)

    # ===== ДАТЫ =====
    date_patterns = [
        r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}",
        r"\d{1,2}\s+(?:январ|феврал|март|апрел|ма[йя]|июн|июл|август|сентябр|октябр|ноябр|декабр)\w*\s+\d{4}",
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, query)
        entities["dates"].extend(matches)

    # ===== ФИО =====
    name_pattern = r"([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)"
    matches = re.findall(name_pattern, query)
    entities["names"].extend(matches)

    # ===== ОРГАНИЗАЦИИ =====
    org_pattern = r'((?:ООО|АО|ОАО|ЗАО|ПАО|ИП)\s+["\']?[А-Яа-яЁё0-9\s]{2,30}?)'
    matches = re.findall(org_pattern, query)
    for match in matches:
        # Берём максимум символов до запятой/точки/предлога
        clean = re.split(r"[,\.!?]|\s+(без|по|на|и|с|в|к|из)\s", match)[0].strip()
        if clean and len(clean) >= 5 and clean not in entities["organizations"]:
            entities["organizations"].append(clean)

    # ===== АДРЕСА =====
    addr_pattern = r"(?:г\.|город|ул\.|улица|пр\.|проспект|д\.|дом)\s+[^,.]+"
    matches = re.findall(addr_pattern, query)
    entities["addresses"].extend(matches)

    return entities


def classify_hybrid(query: str) -> dict:
    """Гибридный классификатор: паттерны + LLM."""
    # 1. Паттерны
    pattern_result = classify_situation(query)

    if pattern_result["confidence"] > 0.7:
        return {**pattern_result, "method": "pattern"}

    # 2. LLM
    llm_result = classify_with_llm(query)

    # Маппинг типов
    type_mapping = {
        "claim_labor_wage": "claim_labor_wage",
        "claim_labor_reinstatement": "claim_labor_reinstatement",
        "claim_consumer": "claim_consumer",
        "claim_divorce": "claim_divorce",
        "claim_alimony": "claim_alimony",
        "claim_civil_general": "claim_civil_general",
        "admin_claim_kas": "admin_claim_kas",
        "complaint_koap": "complaint_koap",
        "application_for_court_order": "application_for_court_order",
        "objection_to_court_order": "objection_to_court_order",
        "appeal_civil": "appeal_civil",
        "cassation_civil": "cassation_civil",
        "special_proceeding_fact": "special_proceeding_fact",
    }

    doc_type = type_mapping.get(llm_result["type"], "unknown")

    # Получаем label из situation_classifier
    try:
        from src.utils.situation_classifier import PATTERNS

        label = PATTERNS.get(doc_type, {}).get("label", llm_result["type"])
    except:
        label = llm_result["type"]

    return {
        "doc_type": doc_type,
        "confidence": llm_result["confidence"],
        "label": label,
        "matched_keywords": [],
        "method": "llm",
        "reason": llm_result.get("reason", ""),
    }


def calculate_claim_duty(doc_type: str, price: float = None) -> dict:
    """Адаптер для duty_calculator."""
    type_mapping = {
        "claim_civil_general": ClaimType.PROPERTY,
        "claim_consumer": ClaimType.CONSUMER,
        "claim_labor_wage": ClaimType.LABOR,
        "claim_labor_reinstatement": ClaimType.LABOR,
        "claim_divorce": ClaimType.DIVORCE,
        "claim_alimony": ClaimType.ALIMONY,
        "admin_claim_kas": ClaimType.NON_PROPERTY,
        "complaint_koap": ClaimType.NON_PROPERTY,
        "special_proceeding_fact": ClaimType.NON_PROPERTY,
    }

    claim_type = type_mapping.get(doc_type, ClaimType.NON_PROPERTY)
    return calculate_duty(claim_type, price, PartyType.INDIVIDUAL)


def get_clarifying_questions(doc_type: str) -> list:
    """Возвращает уточняющие вопросы для типа документа."""
    questions_map = {
        "claim_civil_general": [
            "Есть ли расписка или договор займа?",
            "Когда были переданы деньги?",
            "Какой срок возврата был оговорён?",
        ],
        "claim_consumer": [
            "Когда вы купили товар?",
            "Есть ли чек или другой документ о покупке?",
            "Какие недостатки вы обнаружили?",
        ],
        "claim_labor_wage": [
            "Как давно задерживают зарплату?",
            "Есть ли трудовой договор?",
            "Обращались ли вы к работодателю с письменным требованием?",
        ],
        "claim_labor_reinstatement": [
            "Когда вас уволили?",
            "По какой статье вас уволили?",
            "Почему вы считаете увольнение незаконным?",
        ],
        "claim_divorce": [
            "Есть ли общие несовершеннолетние дети?",
            "Есть ли спор о детях (с кем будут жить)?",
            "Есть ли совместное имущество, которое нужно разделить?",
        ],
        "claim_alimony": [
            "Сколько у вас детей?",
            "Какого они возраста?",
            "Есть ли соглашение об алиментах?",
        ],
        "admin_claim_kas": [
            "Какой орган отказал в предоставлении услуги?",
            "Когда вы обращались?",
            "Есть ли письменный отказ?",
        ],
        "complaint_koap": [
            "Когда было вынесено постановление?",
            "По какой статье КоАП?",
            "Почему вы не согласны с постановлением?",
        ],
    }
    return questions_map.get(doc_type, ["Уточните детали ситуации."])


def analyze_request(query: str) -> dict:
    """Полный анализ запроса пользователя."""
    print(f"\n{'='*70}")
    print(f"📝 Запрос: '{query}'")
    print(f"{'='*70}")

    # 1. Классификация
    classification = classify_hybrid(query)
    print(f"\n🎯 Классификация:")
    print(f"   Тип: {classification['label']}")
    print(f"   Код: {classification['doc_type']}")
    print(f"   Уверенность: {classification['confidence']:.0%}")
    print(f"   Источник: {classification['method']}")

    # 2. Извлечение сущностей
    entities = extract_entities(query)
    print(f"\n🔍 Извлечённые сущности:")
    if entities["sums"]:
        print(f"   💰 Суммы: {entities['sums']}")
    if entities["dates"]:
        print(f"   📅 Даты: {entities['dates']}")
    if entities["names"]:
        print(f"   👤 ФИО: {entities['names']}")
    if entities["organizations"]:
        print(f"   🏢 Организации: {entities['organizations']}")
    if entities["addresses"]:
        print(f"   📍 Адреса: {entities['addresses']}")
    if not any(entities.values()):
        print(f"   (не найдены)")

    # 3. Уточняющие вопросы
    questions = get_clarifying_questions(classification["doc_type"])
    print(f"\n❓ Уточняющие вопросы:")
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")

    # 4. Госпошлина
    price = entities["sums"][0] if entities["sums"] else None
    duty_result = calculate_claim_duty(classification["doc_type"], price)
    print(f"\n💰 Госпошлина:")
    print(f"   Сумма: {duty_result['duty']:,.2f} ₽")
    print(f"   Формула: {duty_result['formula']}")

    return {
        "query": query,
        "classification": classification,
        "entities": entities,
        "duty": duty_result,
        "questions": questions,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("ТЕСТЫ AI-АГЕНТА (улучшенная версия)")
    print("=" * 70)

    tests = [
        "Сосед занял 100 000 рублей и не возвращает уже год",
        "Купил телефон за 50 000, сломался через неделю, хочу вернуть деньги",
        "Меня уволили из ООО Ромашка без причины, я там 10 лет отработал",
        "Муж не платит алименты на двоих детей",
        "Хочу развестись с женой, есть общий ребёнок 5 лет",
    ]

    for query in tests:
        result = analyze_request(query)
